from __future__ import annotations

import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import add_request_logging_middleware
from app.routers.health import router as health_router
from app.routers import auth as auth_router_module
from app.routers import career_readiness as career_readiness_router_module
from app.routers import dashboard as dashboard_router_module
from app.routers import recommendations as recommendations_router_module
from app.routers import roadmaps as roadmaps_router_module
from app.routers import skill_gap as skill_gap_router_module
from app.routers import profile as profile_router_module
from app.utils.logging import configure_logging

settings = get_settings()
logger = logging.getLogger("skillsync_ai")


def _refresh_jobs() -> None:
    """Run one provider refresh in a dedicated database session."""
    from app.database.session import SessionLocal
    from app.integrations.providers.adzuna import AdzunaProvider
    from app.repositories.job_repository import JobRepository
    from app.services.job_ingestion_service import JobIngestionService
    from app.services.job_normalization import JobNormalizationService

    providers = []
    if "adzuna" in str(settings.job_providers).lower():
        providers.append(AdzunaProvider(
            app_id=settings.adzuna_app_id,
            api_key=settings.adzuna_api_key,
            base_url=settings.adzuna_base_url,
            country=settings.adzuna_country,
            timeout=settings.job_timeout_seconds,
        ))
    if not providers or not any(provider.is_configured for provider in providers):
        return
    db = SessionLocal()
    try:
        JobIngestionService(providers, JobRepository(db), JobNormalizationService()).ingest(
            limit_per_provider=min(settings.job_refresh_limit, 200)
        )
    finally:
        db.close()


async def _job_refresh_loop() -> None:
    while True:
        await asyncio.sleep(max(1, settings.job_refresh_minutes) * 60)
        try:
            await asyncio.to_thread(_refresh_jobs)
        except Exception as exc:  # pragma: no cover - background resilience
            logger.warning("Scheduled job refresh failed: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting %s v%s in %s mode", settings.app_name, settings.app_version, settings.environment)
    if settings.auto_seed_data:
        try:
            from app.services.seed_service import seed_initial_data_if_empty

            seed_initial_data_if_empty()
        except Exception as exc:
            logger.warning("Optional database seeding notice: %s", exc)
    refresh_task = None
    if settings.job_scheduler_enabled and settings.job_ingestion_enabled:
        refresh_task = asyncio.create_task(_job_refresh_loop())
    try:
        yield
    finally:
        if refresh_task:
            refresh_task.cancel()
            try:
                await refresh_task
            except asyncio.CancelledError:
                pass
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="SkillSync AI backend foundation.",
    lifespan=lifespan,
    openapi_url=settings.openapi_url if settings.openapi_url else None,
    docs_url=settings.docs_url if settings.docs_url else None,
    redoc_url=settings.redoc_url if settings.redoc_url else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$",
    allow_credentials=settings.allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
add_request_logging_middleware(app)
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router_module.router, prefix=f"{settings.api_prefix}/auth")
app.include_router(career_readiness_router_module.router, prefix=settings.api_prefix)
app.include_router(dashboard_router_module.router, prefix=settings.api_prefix)
app.include_router(recommendations_router_module.router, prefix=settings.api_prefix)
app.include_router(roadmaps_router_module.router, prefix=settings.api_prefix)
app.include_router(skill_gap_router_module.router, prefix=settings.api_prefix)
app.include_router(profile_router_module.router, prefix=settings.api_prefix)

# resume router
from app.routers import resumes as resumes_router_module
app.include_router(resumes_router_module.router, prefix=settings.api_prefix)

# jobs router
from app.routers import jobs as jobs_router_module
app.include_router(jobs_router_module.router, prefix=settings.api_prefix)

# applications router
from app.routers import applications as applications_router_module
app.include_router(applications_router_module.router, prefix=settings.api_prefix)

# candidates router
from app.routers import candidates as candidates_router_module
app.include_router(candidates_router_module.router, prefix=settings.api_prefix)

# courses router
from app.routers import courses as courses_router_module
app.include_router(courses_router_module.router, prefix=settings.api_prefix)

# admin router
from app.routers import admin as admin_router_module
app.include_router(admin_router_module.router, prefix=settings.api_prefix)



@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "SkillSync AI API is running."}
