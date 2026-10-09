from __future__ import annotations

from fastapi import APIRouter

from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.services.recommendation_engine import RecommendationEngineService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/generate", response_model=RecommendationResponse)
def generate_recommendations(payload: RecommendationRequest):
    service = RecommendationEngineService()
    result = service.generate(payload.model_dump())
    return result
