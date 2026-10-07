from __future__ import annotations

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db_session
from app.dependencies.auth import require_roles
from app.dependencies.authorization import ensure_job_management_access
from app.models.models import Job, User, Resume, UserSkill, Skill
from app.services.semantic_job_matching import SemanticJobMatchingService

router = APIRouter(prefix="/candidates", tags=["Candidates"])


class CandidateMatchOut(BaseModel):
    user_id: int
    full_name: str
    email: str
    match_score: float
    semantic_score: float
    skill_score: float
    experience_score: float
    education_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    concerns: List[str]


@router.get("/ranked/{job_id}", response_model=List[CandidateMatchOut])
def get_ranked_candidates_for_job(
    job_id: int,
    current_user: User = Depends(require_roles("EMPLOYER", "ADMIN")),
    db: Session = Depends(get_db_session)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    ensure_job_management_access(current_user, job)

    matcher = SemanticJobMatchingService()
    candidates = db.query(User).filter(User.role == "CANDIDATE").all()

    job_dict = {
        "title": job.title,
        "description": job.description or "",
        "required_skills": [js.skill.name for js in job.required_skills if js.skill],
        "preferred_skills": [],
        "experience_required_years": 1.0,
    }

    results = []
    for cand in candidates:
        user_skills = [us.skill.name for us in cand.skills if us.skill]
        resume = db.query(Resume).filter(Resume.user_id == cand.id, Resume.is_active == True).first()
        resume_text = resume.parsed_text if resume else ""

        cand_profile = {
            "skills": user_skills,
            "resume_text": resume_text or " ".join(user_skills),
            "experience_years": 1.0,
            "project_count": len(cand.projects)
        }

        match_result = matcher.calculate(cand_profile, job_dict)
        results.append(CandidateMatchOut(
            user_id=cand.id,
            full_name=cand.full_name or cand.email,
            email=cand.email,
            match_score=match_result["overall_match_score"],
            semantic_score=match_result["score_breakdown"]["semantic_similarity"],
            skill_score=match_result["score_breakdown"]["required_skill_coverage"],
            experience_score=match_result["score_breakdown"]["experience_relevance"],
            education_score=100.0,
            matched_skills=match_result["matched_skills"],
            missing_skills=match_result["missing_skills"],
            strengths=match_result["strengths"],
            concerns=match_result["potential_concerns"]
        ))

    results.sort(key=lambda x: x.match_score, reverse=True)
    return results
