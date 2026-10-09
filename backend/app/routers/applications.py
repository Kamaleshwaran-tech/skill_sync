from __future__ import annotations

from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database.session import get_db_session
from app.dependencies.auth import get_current_user, require_roles
from app.dependencies.authorization import ensure_job_management_access
from app.models.models import Application, Job, Resume, User

router = APIRouter(prefix="/applications", tags=["Applications"])


class ApplicationCreate(BaseModel):
    job_id: int
    resume_id: Optional[int] = None
    cover_letter: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: Literal["PENDING", "SHORTLISTED", "REJECTED", "HIRED"]


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    resume_id: Optional[int]
    status: str
    match_score: Optional[float]
    cover_letter: Optional[str]
    applied_at: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


@router.post("/", response_model=ApplicationOut)
def apply_for_job(
    payload: ApplicationCreate,
    current_user: User = Depends(require_roles("CANDIDATE", "ADMIN")),
    db: Session = Depends(get_db_session)
):
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if payload.resume_id is not None:
        resume = db.query(Resume).filter(
            Resume.id == payload.resume_id,
            Resume.user_id == current_user.id,
        ).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

    existing = db.query(Application).filter(
        Application.job_id == payload.job_id,
        Application.candidate_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied for this job")

    application = Application(
        job_id=payload.job_id,
        candidate_id=current_user.id,
        resume_id=payload.resume_id,
        cover_letter=payload.cover_letter,
        status="PENDING"
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return ApplicationOut(
        id=application.id,
        job_id=application.job_id,
        candidate_id=application.candidate_id,
        resume_id=application.resume_id,
        status=application.status,
        match_score=application.match_score,
        cover_letter=application.cover_letter,
        applied_at=str(application.applied_at),
        job_title=job.title,
        company_name=job.company
    )


@router.get("/my-applications", response_model=List[ApplicationOut])
def get_my_applications(
    current_user: User = Depends(require_roles("EMPLOYER", "ADMIN")),
    db: Session = Depends(get_db_session)
):
    apps = db.query(Application).filter(Application.candidate_id == current_user.id).all()
    results = []
    for app in apps:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        results.append(ApplicationOut(
            id=app.id,
            job_id=app.job_id,
            candidate_id=app.candidate_id,
            resume_id=app.resume_id,
            status=app.status,
            match_score=app.match_score,
            cover_letter=app.cover_letter,
            applied_at=str(app.applied_at),
            job_title=job.title if job else "Unknown",
            company_name=job.company if job else "N/A"
        ))
    return results


@router.get("/job/{job_id}", response_model=List[ApplicationOut])
def get_job_applications(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    ensure_job_management_access(current_user, job)

    apps = db.query(Application).filter(Application.job_id == job_id).all()
    results = []
    for app in apps:
        candidate = db.query(User).filter(User.id == app.candidate_id).first()
        results.append(ApplicationOut(
            id=app.id,
            job_id=app.job_id,
            candidate_id=app.candidate_id,
            resume_id=app.resume_id,
            status=app.status,
            match_score=app.match_score,
            cover_letter=app.cover_letter,
            applied_at=str(app.applied_at),
            job_title=job.title,
            company_name=job.company,
            candidate_name=candidate.full_name if candidate else "Anonymous",
            candidate_email=candidate.email if candidate else "N/A"
        ))
    return results


@router.patch("/{application_id}/status")
def update_application_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    current_user: User = Depends(require_roles("EMPLOYER", "ADMIN")),
    db: Session = Depends(get_db_session)
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    job = db.query(Job).filter(Job.id == app.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    ensure_job_management_access(current_user, job)

    app.status = payload.status.upper()
    db.commit()
    return {"message": "Application status updated successfully", "status": app.status}
