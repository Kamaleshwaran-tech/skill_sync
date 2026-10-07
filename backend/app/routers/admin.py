from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db_session
from app.dependencies.auth import require_roles
from app.models.models import User, Job, Company, Skill, AuditLog

router = APIRouter(prefix="/admin", tags=["Admin"])


class SystemStatsOut(BaseModel):
    total_users: int
    total_candidates: int
    total_employers: int
    total_jobs: int
    total_companies: int
    total_skills: int


@router.get("/stats", response_model=SystemStatsOut)
def get_system_stats(
    current_user: User = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db_session)
):
    return SystemStatsOut(
        total_users=db.query(User).count(),
        total_candidates=db.query(User).filter(User.role == "CANDIDATE").count(),
        total_employers=db.query(User).filter(User.role == "EMPLOYER").count(),
        total_jobs=db.query(Job).count(),
        total_companies=db.query(Company).count(),
        total_skills=db.query(Skill).count()
    )


@router.get("/users")
def list_users(
    current_user: User = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db_session)
):
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role, "is_active": u.is_active, "created_at": str(u.created_at)} for u in users]


@router.get("/companies")
def list_companies(
    current_user: User = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db_session)
):
    companies = db.query(Company).all()
    return [{"id": c.id, "name": c.name, "website": c.website, "location": c.location, "created_at": str(c.created_at)} for c in companies]
