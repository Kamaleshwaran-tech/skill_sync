from io import BytesIO
from datetime import datetime, timedelta, timezone
from sqlalchemy import and_, or_
from pathlib import Path
import logging
import uuid
import zipfile
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.config.settings import get_settings
from app.database.session import get_db_session
from app.dependencies.auth import get_current_user
from app.models.models import Resume, ResumeAnalysis, ResumeMatchRun
from app.schemas.resume import ResumeOut
from app.schemas.resume_analysis import ResumeAnalysisOut
from app.services.resume_parser import ResumeParser

router = APIRouter(prefix="/resumes", tags=["Resumes"])
logger = logging.getLogger(__name__)


def owned_resume(db, user, resume_id):
    resume = db.query(Resume).filter_by(id=resume_id, user_id=user.id).first()
    if not resume:
        raise HTTPException(404, "Resume not found")
    return resume


def _path(resume):
    root = Path(get_settings().resume_storage_dir).resolve()
    path = Path(resume.storage_path or "").resolve()
    if path.parent != root:
        raise HTTPException(404, "Resume file unavailable")
    return path


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    name = (file.filename or "").strip()
    if not name or "/" in name or "\\" in name:
        raise HTTPException(400, "Invalid resume filename")
    extension = Path(name).suffix.lower()
    if extension not in {".pdf", ".docx"}:
        raise HTTPException(400, "Only PDF and DOCX files are supported")
    limit = get_settings().resume_max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if not data or len(data) > limit:
        raise HTTPException(
            400,
            f"File must contain data and be at most {get_settings().resume_max_upload_mb} MB",
        )
    if extension == ".pdf" and not data.startswith(b"%PDF-"):
        raise HTTPException(400, "Invalid PDF file")
    if extension == ".docx":
        try:
            with zipfile.ZipFile(BytesIO(data)) as archive:
                if (
                    "word/document.xml" not in archive.namelist()
                    or "[Content_Types].xml" not in archive.namelist()
                ):
                    raise ValueError()
                if (
                    len(archive.infolist()) > 1000
                    or sum(e.file_size for e in archive.infolist()) > 25 * 1024 * 1024
                ):
                    raise ValueError()
        except (ValueError, zipfile.BadZipFile):
            raise HTTPException(400, "Invalid DOCX or expanded document exceeds 25 MB")
    root = Path(get_settings().resume_storage_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / (uuid.uuid4().hex + extension)
    path.write_bytes(data)
    resume = Resume(
        user_id=user.id,
        filename=name,
        storage_path=str(path),
        file_type=extension[1:],
        file_size=len(data),
        status="UPLOADED",
        is_active=False,
    )
    try:
        db.add(resume)
        db.commit()
        db.refresh(resume)
    except Exception:
        db.rollback()
        path.unlink(missing_ok=True)
        raise
    return resume


@router.get("/", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    return db.query(Resume).filter_by(user_id=user.id).order_by(Resume.id.desc()).all()


@router.post("/{resume_id}/analyze", response_model=ResumeOut)
def analyze_resume(
    resume_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    resume = owned_resume(db, user, resume_id)
    # Completed snapshots are immutable. Re-upload to change the evidence.
    latest = (
        db.query(ResumeAnalysis)
        .filter_by(resume_id=resume.id)
        .order_by(ResumeAnalysis.id.desc())
        .first()
    )
    if (
        resume.status == "COMPLETED"
        and latest
        and (latest.profile or {}).get("parser_version") == "evidence-v1"
    ):
        return resume
    path = _path(resume)
    if not path.exists():
        raise HTTPException(404, "Resume file unavailable")
    resume_id, user_id = resume.id, user.id
    started = datetime.now(timezone.utc).replace(tzinfo=None)
    stale = or_(
        Resume.processing_started_at.is_(None),
        Resume.processing_started_at < started - timedelta(minutes=5),
    )
    changed = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            or_(
                Resume.status.in_(["UPLOADED", "FAILED", "COMPLETED"]),
                and_(Resume.status == "PROCESSING", stale),
            ),
        )
        .update(
            {"status": "PROCESSING", "processing_started_at": started},
            synchronize_session=False,
        )
    )
    db.commit()
    if not changed:
        raise HTTPException(
            409,
            "This resume is already being analysed. After an interrupted server, retry after five minutes.",
        )
    try:
        result = ResumeParser().extract(str(path))
        # The timestamp is the processing lease. An expired worker cannot overwrite a retry.
        changed = (
            db.query(Resume)
            .filter_by(id=resume_id, status="PROCESSING", processing_started_at=started)
            .update(
                {
                    "parsed_text": result["profile"]["raw_text"],
                    "status": "COMPLETED",
                    "processing_started_at": None,
                },
                synchronize_session=False,
            )
        )
        if not changed:
            raise HTTPException(
                409,
                "Processing was superseded or the resume was deleted. Reload the resume list.",
            )
        db.add(
            ResumeAnalysis(
                resume_id=resume_id, profile=result["profile"], confidence=None
            )
        )
        db.query(Resume).filter_by(user_id=user_id).update({"is_active": False})
        db.query(Resume).filter_by(id=resume_id).update({"is_active": True})
        db.commit()
        db.refresh(resume)
        return resume
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        db.query(Resume).filter_by(
            id=resume_id, status="PROCESSING", processing_started_at=started
        ).update(
            {"status": "FAILED", "processing_started_at": None},
            synchronize_session=False,
        )
        db.commit()
        if isinstance(exc, ValueError):
            raise HTTPException(422, str(exc)) from None
        logger.warning("Resume parsing failed (%s)", type(exc).__name__)
        raise HTTPException(
            422,
            "Unable to read this document. Try a readable, unencrypted PDF or DOCX.",
        ) from None


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisOut)
def get_analysis(
    resume_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    owned_resume(db, user, resume_id)
    analysis = (
        db.query(ResumeAnalysis)
        .filter_by(resume_id=resume_id)
        .order_by(ResumeAnalysis.id.desc())
        .first()
    )
    if not analysis:
        raise HTTPException(404, "Resume has not been analysed yet")
    return analysis


@router.get("/{resume_id}/file")
def get_file(
    resume_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    resume = owned_resume(db, user, resume_id)
    path = _path(resume)
    if not path.exists():
        raise HTTPException(404, "Resume file unavailable")
    return FileResponse(
        path,
        filename=resume.filename,
        media_type="application/pdf"
        if resume.file_type == "pdf"
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    resume = owned_resume(db, user, resume_id)
    path = _path(resume)
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=5)
    changed = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            or_(
                Resume.status != "PROCESSING",
                Resume.processing_started_at.is_(None),
                Resume.processing_started_at < cutoff,
            ),
        )
        .update(
            {"status": "DELETING", "processing_started_at": None},
            synchronize_session=False,
        )
    )
    if not changed:
        raise HTTPException(
            409,
            "Wait for processing before deleting; interrupted processing expires after five minutes.",
        )
    db.query(ResumeMatchRun).filter_by(resume_id=resume_id, user_id=user.id).delete()
    db.query(ResumeAnalysis).filter_by(resume_id=resume_id).delete()
    db.delete(resume)
    db.commit()
    path.unlink(missing_ok=True)
    return {"detail": "Resume and its saved matching results deleted"}
