from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.config.settings import get_settings, COUNTRIES
from app.database.session import get_db_session
from app.dependencies.auth import get_current_user
from app.models.models import ResumeAnalysis, ResumeMatchRun
from app.routers.resumes import owned_resume
from app.services.adzuna import AdzunaProvider, AdzunaError
from app.services.job_matching import rank_jobs

router = APIRouter(prefix="/jobs", tags=["Resume job matching"])


class SearchRequest(BaseModel):
    resume_id: int = Field(gt=0)
    query: str = Field(default="", max_length=120)
    location: str = Field(default="", max_length=120)
    country: Literal["in", "gb", "us", "au", "ca"] | None = None
    max_days: int = Field(default=30, ge=1, le=90)
    limit: Literal[20, 50, 100] = 50
    model_config = ConfigDict(extra="forbid")


@router.get("/status")
def provider_status(user=Depends(get_current_user)):
    provider = AdzunaProvider()
    return {
        "provider": provider.source,
        "configured": provider.is_configured,
        "country": get_settings().adzuna_country,
        "countries": COUNTRIES,
        "max_results": 100,
        "sends_resume_to_provider": False,
    }


@router.post("/search")
def search_matches(
    payload: SearchRequest,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    resume = owned_resume(db, user, payload.resume_id)
    if resume.status != "COMPLETED":
        raise HTTPException(409, "Analyse this resume before matching jobs")
    analysis = (
        db.query(ResumeAnalysis)
        .filter_by(resume_id=resume.id)
        .order_by(ResumeAnalysis.id.desc())
        .first()
    )
    if not analysis or (analysis.profile or {}).get("parser_version") != "evidence-v1":
        raise HTTPException(
            409,
            "Re-analyse this older resume with the current evidence-based parser first",
        )
    resume_id, analysis_id, user_id = resume.id, analysis.id, user.id
    query = payload.query.strip() or (analysis.profile or {}).get("suggested_query", "")
    if not query:
        raise HTTPException(
            422,
            "Enter a job title or keyword; no reliable search suggestion could be extracted",
        )
    country = payload.country or get_settings().adzuna_country
    provider = AdzunaProvider()
    try:
        fetched = provider.fetch_jobs(
            query, payload.location.strip(), country, payload.max_days, payload.limit
        )
    except AdzunaError as exc:
        raise HTTPException(
            exc.status, detail={"code": exc.code, "message": exc.message}
        ) from None
    jobs, skipped = rank_jobs(
        analysis.profile, fetched["results"], country, payload.max_days
    )
    result = {
        "resume_id": resume.id,
        "resume_filename": resume.filename,
        "analysis_id": analysis.id,
        "provider": fetched["source"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "location": payload.location.strip(),
        "country": country,
        "max_days": payload.max_days,
        "requested_limit": payload.limit,
        "provider_total": fetched["provider_count"],
        "fetched_count": len(fetched["results"]),
        "scored_count": len(jobs),
        "skipped_count": skipped,
        "scope": "Ranked only the bounded set returned for this query, not every job in the market.",
        "score_version": "evidence-overlap-v1",
        "score_notice": "Heuristic evidence overlap, not a probability of getting hired. Confirm requirements and vacancy status on Adzuna.",
        "jobs": jobs,
    }
    # Recheck ownership/existence after the external call (the user may have deleted the resume).
    db.expire_all()
    current = owned_resume(db, user, resume_id)
    latest = (
        db.query(ResumeAnalysis.id)
        .filter_by(resume_id=resume_id)
        .order_by(ResumeAnalysis.id.desc())
        .first()
    )
    if current.status != "COMPLETED" or not latest or latest[0] != analysis_id:
        raise HTTPException(
            409, "Resume analysis changed during the search. Reload and search again."
        )
    run = ResumeMatchRun(
        user_id=user_id, resume_id=resume_id, analysis_id=analysis_id, result=result
    )
    try:
        db.add(run)
        db.commit()
        db.refresh(run)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409, "Resume changed during the search. Reload and search again."
        ) from None
    return {**result, "run_id": run.id, "from_saved_search": False}


@router.get("/matches/{resume_id}")
def saved_matches(
    resume_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    owned_resume(db, user, resume_id)
    latest = (
        db.query(ResumeAnalysis.id)
        .filter_by(resume_id=resume_id)
        .order_by(ResumeAnalysis.id.desc())
        .first()
    )
    run = (
        db.query(ResumeMatchRun)
        .filter_by(
            user_id=user.id,
            resume_id=resume_id,
            analysis_id=latest[0] if latest else -1,
        )
        .order_by(ResumeMatchRun.id.desc())
        .first()
    )
    return {
        "result": {**run.result, "run_id": run.id, "from_saved_search": True}
        if run
        else None
    }
