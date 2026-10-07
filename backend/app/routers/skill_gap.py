from __future__ import annotations

from fastapi import APIRouter

from app.schemas.skill_gap import SkillGapAnalysisRequest, SkillGapAnalysisResponse
from app.services.skill_gap_analysis import SkillGapAnalysisService

router = APIRouter(prefix="/skill-gap", tags=["Skill Gap"])


@router.post("/analyze", response_model=SkillGapAnalysisResponse)
def analyze_skill_gap(payload: SkillGapAnalysisRequest):
    service = SkillGapAnalysisService()
    jobs = service.analyze_jobs(
        student_skills=[item.model_dump() if hasattr(item, "model_dump") else item for item in payload.student_skills],
        jobs=[job.model_dump() if hasattr(job, "model_dump") else job for job in payload.jobs],
        job_market_demand=payload.job_market_demand,
        prerequisites=payload.prerequisites,
    )
    return {"jobs": jobs}
