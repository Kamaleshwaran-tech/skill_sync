from __future__ import annotations

from fastapi import APIRouter

from app.schemas.career_readiness import CareerReadinessRequest, CareerReadinessResponse
from app.services.career_readiness import CareerReadinessService

router = APIRouter(prefix="/career-readiness", tags=["Career Readiness"])


@router.post("/score", response_model=CareerReadinessResponse)
def score_career_readiness(payload: CareerReadinessRequest):
    service = CareerReadinessService()
    result = service.calculate(payload.model_dump())
    return result
