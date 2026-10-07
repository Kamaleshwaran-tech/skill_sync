from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config.settings import get_settings
from app.dependencies.db import get_database_status
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check(database_status: dict = Depends(get_database_status)) -> HealthResponse:
    return HealthResponse(
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        database={
            "status": "connected" if database_status["healthy"] else "unavailable",
            "message": database_status["message"],
        },
    )
