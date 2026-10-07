from __future__ import annotations

import os
import uuid
import zipfile
from pathlib import Path
from typing import IO
from io import BytesIO

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.database.session import get_db_session
from app.dependencies.auth import get_current_user
from app.schemas.resume import ResumeOut
from app.schemas.resume_analysis import ResumeAnalysisOut
from app.models.models import Resume
from app.utils.storage_local import LocalStorage

router = APIRouter(prefix="/resumes", tags=["Resumes"])
settings = get_settings()

# initialize local storage
storage = LocalStorage(settings.resume_storage_dir)

ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


def _validate_file(upload: UploadFile, data: bytes) -> str:
    if not upload.filename or not upload.filename.strip():
        raise HTTPException(status_code=400, detail="Resume filename is required.")

    sanitized_name = os.path.basename(upload.filename)
    if sanitized_name != upload.filename:
        raise HTTPException(status_code=400, detail="Resume filename contains invalid path characters.")

    ct = upload.content_type
    ext = ALLOWED_CONTENT_TYPES.get(ct)
    if not ext:
        lower = sanitized_name.lower()
        if lower.endswith('.pdf'):
            ext = '.pdf'
        elif lower.endswith('.docx'):
            ext = '.docx'
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF and DOCX are allowed.")
    if ext == ".pdf" and not data.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")
    if ext == ".docx":
        try:
            with zipfile.ZipFile(BytesIO(data)) as archive:
                if "[Content_Types].xml" not in archive.namelist() or not any(
                    entry.startswith("word/") for entry in archive.namelist()
                ):
                    raise ValueError("Missing DOCX document entries")
        except (OSError, ValueError, zipfile.BadZipFile):
            raise HTTPException(status_code=400, detail="The uploaded file is not a valid DOCX document.")
    return ext


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db_session), current_user=Depends(get_current_user)):
    # validate size: UploadFile doesn't provide size readily; read into memory up to limit
    max_bytes = settings.resume_max_upload_mb * 1024 * 1024
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Resume file is empty.")
    if len(data) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed size of {settings.resume_max_upload_mb} MB")

    # validate type
    ext = _validate_file(file, data)

    # generate unique filename
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest_rel = unique_name

    # save to storage using binary buffer
    storage.save(BytesIO(data), dest_rel)

    # persist metadata
    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        storage_path=str(Path(settings.resume_storage_dir) / dest_rel),
        file_type=ext.replace('.', ''),
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
        storage.delete(dest_rel)
        raise HTTPException(status_code=500, detail="Unable to save resume metadata.")
    return resume


@router.get("/", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db_session), current_user=Depends(get_current_user)):
    items = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.uploaded_at.desc()).all()
    return items


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, db: Session = Depends(get_db_session), current_user=Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db_session), current_user=Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    # delete file from storage if present
    if resume.storage_path:
        try:
            p = Path(resume.storage_path)
            if p.exists():
                p.unlink()
        except Exception:
            pass
    db.delete(resume)
    db.commit()
    return {"detail": "deleted"}


@router.post("/{resume_id}/analyze", response_model=ResumeOut)
def analyze_resume(resume_id: int, db: Session = Depends(get_db_session), current_user=Depends(get_current_user)):
    from app.services.resume_parser import ResumeParser
    from app.models.models import ResumeAnalysis, Skill, UserSkill, CareerReadiness, CandidateProfile, Job
    from sqlalchemy import func

    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # set processing
    resume.status = "PROCESSING"
    db.add(resume)
    db.commit()
    db.refresh(resume)

    parser = ResumeParser()
    try:
        # choose extractor based on file extension
        text = ""
        if resume.storage_path and resume.storage_path.lower().endswith('.pdf'):
            try:
                text = parser.extract_text_from_pdf(resume.storage_path)
            except Exception:
                text = resume.parsed_text or ""
        elif resume.storage_path and resume.storage_path.lower().endswith('.docx'):
            try:
                text = parser.extract_text_from_docx(resume.storage_path)
            except Exception:
                text = resume.parsed_text or ""
        else:
            text = resume.parsed_text or ""

        result = parser.extract_structured(text)
        profile = result.get('profile') or {}
        confidence = result.get('confidence')
        if not profile.get("raw_text") or len(profile["raw_text"].strip()) < 40:
            raise ValueError("No readable resume content was extracted. Please upload a text-based PDF or DOCX.")

        # persist analysis
        analysis = ResumeAnalysis(resume_id=resume.id, profile=profile, confidence=confidence)
        db.add(analysis)
        # optionally persist parsed text
        resume.parsed_text = profile.get('raw_text') or text

        # Replace skills extracted from the prior resume while retaining skills
        # explicitly added by the user or another verified source.
        db.query(UserSkill).filter(
            UserSkill.user_id == current_user.id,
            UserSkill.source == "resume",
        ).delete(synchronize_session=False)
        seen_skill_ids: set[int] = {
            skill_id for (skill_id,) in db.query(UserSkill.skill_id).filter(UserSkill.user_id == current_user.id).all()
        }
        all_skill_names: list[str] = []

        def add_skill_to_user(skill_name: str, category: str):
            clean_name = skill_name.strip()
            if not clean_name:
                return
            all_skill_names.append(clean_name)
            # Find or create skill in master taxonomy (case-insensitive check)
            skill = db.query(Skill).filter(func.lower(Skill.name) == clean_name.lower()).first()
            if not skill:
                skill = Skill(name=clean_name, category=category)
                db.add(skill)
                db.flush()
                db.refresh(skill)
            if skill.id not in seen_skill_ids:
                seen_skill_ids.add(skill.id)
                db.add(UserSkill(user_id=current_user.id, skill_id=skill.id, proficiency=None, source='resume'))

        # Add detected technical skills to master skills and user skills
        tech = profile.get('technical_skills', [])
        for s in tech:
            name = s.get('name') if isinstance(s, dict) else str(s)
            if name:
                add_skill_to_user(name, 'technical')

        # Add detected soft skills to master skills and user skills
        soft = profile.get('soft_skills', [])
        for s_item in soft:
            s_name = s_item.get('name') if isinstance(s_item, dict) else str(s_item)
            if s_name:
                add_skill_to_user(s_name, 'soft')

        # Update candidate profile if available
        personal_info = profile.get("personal_info") or {}
        candidate_name = profile.get("name")
        if candidate_name and candidate_name != "Student Candidate" and (not current_user.full_name or current_user.full_name.lower() in ["student", "candidate", "user", ""]):
            current_user.full_name = candidate_name
            db.add(current_user)

        cp = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
        if not cp:
            cp = CandidateProfile(user_id=current_user.id)
            db.add(cp)
        if personal_info.get("phone"):
            cp.phone = personal_info["phone"]
        if personal_info.get("location"):
            cp.location = personal_info["location"]
        if personal_info.get("linkedin"):
            cp.linkedin_url = personal_info["linkedin"]
        if personal_info.get("portfolio"):
            cp.github_url = personal_info["portfolio"]
        if profile.get("summary"):
            cp.bio = profile["summary"]

        # Dynamically compute and store CareerReadiness
        user_skill_count = len(seen_skill_ids)
        tech_score = float(min(round(user_skill_count * 3.5 + 25), 95))
        res_conf = confidence if confidence is not None else 0.88
        res_score = float(round(res_conf * 100, 1))

        projects_list = profile.get("projects") or []
        proj_score = float(min(round(len(projects_list) * 20.0 + 45.0), 92)) if projects_list else 70.0

        exp_list = profile.get("experience") or []
        exp_score = float(min(round(len(exp_list) * 25.0 + 40.0), 90)) if exp_list else 65.0

        active_jobs = db.query(Job).filter(Job.is_active.is_(True)).order_by(Job.created_at.desc()).limit(15).all()
        ind_score = 75.0
        if active_jobs:
            from app.services.semantic_job_matching import SemanticJobMatchingService
            matcher = SemanticJobMatchingService()
            user_skill_names = list(set(all_skill_names))
            match_scores = []
            for j in active_jobs:
                req_names = [js.skill.name for js in j.required_skills if js.skill and js.skill_type == "required"]
                pref_names = [js.skill.name for js in j.required_skills if js.skill and js.skill_type == "preferred"]
                m_res = matcher.calculate(
                    {"skills": user_skill_names, "resume_text": text},
                    {"description": j.description or "", "required_skills": req_names, "preferred_skills": pref_names},
                )
                score_val = m_res.get("overall_match_score", 0)
                if score_val > 0:
                    match_scores.append(score_val)
            if match_scores:
                ind_score = float(round(sum(match_scores) / len(match_scores), 1))

        overall_score = float(round(
            tech_score * 0.30 +
            res_score * 0.25 +
            ind_score * 0.25 +
            proj_score * 0.10 +
            exp_score * 0.10,
            1
        ))

        cr = db.query(CareerReadiness).filter(CareerReadiness.user_id == current_user.id).order_by(CareerReadiness.updated_at.desc()).first()
        if not cr:
            cr = CareerReadiness(user_id=current_user.id)
            db.add(cr)
        cr.overall_score = overall_score
        cr.technical_score = tech_score
        cr.industry_score = ind_score
        cr.resume_score = res_score
        cr.project_score = proj_score
        cr.experience_score = exp_score

        db.query(Resume).filter(Resume.user_id == current_user.id).update({Resume.is_active: False})
        resume.is_active = True
        resume.status = "COMPLETED"
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
    except Exception as exc:
        # mark failed
        import traceback
        traceback.print_exc()
        db.rollback()
        resume.status = "FAILED"
        db.add(resume)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {str(exc)}")


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisOut)
def get_resume_analysis(resume_id: int, db: Session = Depends(get_db_session), current_user=Depends(get_current_user)):
    from app.models.models import ResumeAnalysis

    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    analysis = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.resume_id == resume.id)
        .order_by(ResumeAnalysis.created_at.desc())
        .first()
    )
    if not analysis and resume.storage_path and Path(resume.storage_path).exists():
        analyze_resume(resume_id=resume.id, db=db, current_user=current_user)
        analysis = (
            db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.resume_id == resume.id)
            .order_by(ResumeAnalysis.created_at.desc())
            .first()
        )
    if not analysis:
        raise HTTPException(status_code=404, detail="Resume analysis is not available yet")
    return analysis


@router.get("/{resume_id}/file")
def download_resume_file(
    resume_id: int,
    db: Session = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """Securely stream/download the resume file. Only the authenticated owner can access it."""
    from fastapi.responses import FileResponse

    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
    ).one_or_none()

    if not resume or not resume.storage_path:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    file_path = Path(resume.storage_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resume file not found on disk")

    media_type = "application/pdf" if resume.file_type.lower() == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=resume.filename,
    )

