from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.database.session import get_db_session
from app.dependencies.auth import get_current_user, require_roles
from app.integrations.providers.additional_provider import AdditionalProvider
from app.integrations.providers.adzuna import AdzunaProvider
from app.repositories.job_repository import JobRepository
from app.services.job_ingestion_service import JobIngestionService
from app.services.job_normalization import JobNormalizationService
from app.services.semantic_job_matching import SemanticJobMatchingService
from app.models.models import Job, JobMatch, MatchDetail, Resume, SkillGap, UserSkill

router = APIRouter(prefix="/jobs", tags=["Jobs"])
settings = get_settings()


class JobMatchRequest(BaseModel):
    resume_id: int
    job_id: int


def _build_providers():
    providers = []
    if "adzuna" in str(settings.job_providers).lower():
        providers.append(
            AdzunaProvider(
                app_id=settings.adzuna_app_id,
                api_key=settings.adzuna_api_key,
                base_url=settings.adzuna_base_url,
                country=settings.adzuna_country,
                timeout=settings.job_timeout_seconds,
            )
        )
    if settings.additional_job_provider_url:
        providers.append(
            AdditionalProvider(
                base_url=settings.additional_job_provider_url,
                api_key=settings.additional_job_provider_api_key,
                timeout=settings.job_timeout_seconds,
            )
        )
    return providers


@router.get("")
@router.get("/")
def list_jobs(
    search: str | None = Query(default=None, max_length=120),
    location: str | None = Query(default=None, max_length=120),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db_session),
):
    repo = JobRepository(db)
    jobs = repo.list_jobs(search=search, location=location, offset=(page - 1) * page_size, limit=page_size)
    # Refresh the shared cache after its TTL; every visitor then sees current
    # results without each page load consuming an Adzuna request.
    if settings.job_ingestion_enabled and (not jobs or repo.needs_refresh(settings.job_refresh_minutes)):
        providers = _build_providers()
        if providers:
            JobIngestionService(
                providers=providers,
                repo=repo,
                normalizer=JobNormalizationService(),
            ).ingest(query=search, location=location, limit_per_provider=min(settings.job_refresh_limit, 200))
            jobs = repo.list_jobs(search=search, location=location, offset=(page - 1) * page_size, limit=page_size)
    return [
        {
            "id": job.id,
            "external_id": job.external_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "description": job.description,
            "posted_date": job.posted_date,
            "url": job.url,
            "required_skills": [item.skill.name for item in job.required_skills if item.skill and item.skill_type == "required"],
            "preferred_skills": [item.skill.name for item in job.required_skills if item.skill and item.skill_type == "preferred"],
        }
        for job in jobs
    ]


@router.post("/match")
def match_resume_to_job(
    payload: JobMatchRequest,
    current_user=Depends(require_roles("CANDIDATE", "ADMIN")),
    db: Session = Depends(get_db_session),
):
    resume = db.query(Resume).filter(
        Resume.id == payload.resume_id,
        Resume.user_id == current_user.id,
        Resume.status == "COMPLETED",
    ).one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="A completed resume was not found")

    job = db.query(Job).filter(Job.id == payload.job_id, Job.is_active.is_(True)).one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Active job not found")

    user_skill_rows = (
        db.query(UserSkill)
        .filter(UserSkill.user_id == current_user.id)
        .all()
    )
    user_skills = [row.skill.name for row in user_skill_rows if row.skill]
    proficiency_by_skill = {row.skill_id: row.proficiency or 0 for row in user_skill_rows}
    required_skills = [row.skill.name for row in job.required_skills if row.skill and row.skill_type == "required"]
    preferred_skills = [row.skill.name for row in job.required_skills if row.skill and row.skill_type == "preferred"]

    result = SemanticJobMatchingService().calculate(
        {
            "skills": user_skills,
            "resume_text": resume.parsed_text or " ".join(user_skills),
            "experience_years": len(current_user.experiences),
            "project_count": len(current_user.projects),
        },
        {
            "description": job.description or "",
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "experience_required_years": 1.0,
            "project_count": 1,
        },
    )

    match = db.query(JobMatch).filter(JobMatch.user_id == current_user.id, JobMatch.job_id == job.id).one_or_none()
    if match is None:
        match = JobMatch(user_id=current_user.id, job_id=job.id)
        db.add(match)
        db.flush()
    else:
        db.query(SkillGap).filter(SkillGap.job_match_id == match.id).delete()
        db.query(MatchDetail).filter(MatchDetail.job_match_id == match.id).delete()
        db.flush()

    match.match_score = result["overall_match_score"]
    match.matched_skills_count = len(result["matched_skills"])
    match.missing_skills_count = len(result["missing_skills"])
    db.add(
        MatchDetail(
            job_match=match,
            semantic_similarity=result["semantic_similarity"],
            required_skill_coverage=result["required_skill_coverage"],
            preferred_skill_coverage=result["preferred_skill_coverage"],
            experience_relevance=result["experience_relevance"],
            project_relevance=result["project_relevance"],
            score_breakdown=result["score_breakdown"],
            strengths=result["strengths"],
            potential_concerns=result["potential_concerns"],
        )
    )
    seen_skill_ids: set[int] = set()
    for job_skill in job.required_skills:
        if not job_skill.skill or job_skill.skill.name not in result["missing_skills"]:
            continue
        if job_skill.skill_id in seen_skill_ids:
            continue
        seen_skill_ids.add(job_skill.skill_id)
        required_proficiency = job_skill.required_proficiency or 0
        current_proficiency = proficiency_by_skill.get(job_skill.skill_id, 0)
        gap_percentage = max(0.0, (required_proficiency - current_proficiency) * 100.0 / max(1, required_proficiency))
        db.add(
            SkillGap(
                job_match=match,
                skill_id=job_skill.skill_id,
                current_proficiency=current_proficiency,
                required_proficiency=required_proficiency,
                gap_percentage=gap_percentage,
                recommendation=f"Build practical experience with {job_skill.skill.name} before applying.",
            )
        )
    db.commit()

    return {
        **result,
        "resume_id": resume.id,
        "job_id": job.id,
        "job_match_id": match.id,
    }


@router.post("/ingest")
def ingest_jobs(
    current_user=Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db_session),
    query: str | None = Query(default=None),
    location: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
):
    if not settings.job_ingestion_enabled:
        raise HTTPException(status_code=503, detail="Job ingestion is disabled")

    providers = _build_providers()
    if not providers:
        return {"created": 0, "skipped": 0, "errors": ["No job providers configured."]}

    service = JobIngestionService(
        providers=providers,
        repo=JobRepository(db),
        normalizer=JobNormalizationService(),
    )
    return service.ingest(query=query, location=location, limit_per_provider=limit)
