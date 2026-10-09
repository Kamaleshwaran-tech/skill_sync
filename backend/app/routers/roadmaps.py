from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.roadmap import LearningRoadmapResponse, RoadmapGenerationRequest
from app.services.gemini_roadmap_service import GeminiRoadmapService

router = APIRouter(prefix="/roadmaps", tags=["Learning Roadmaps"])


@router.post("/generate", response_model=LearningRoadmapResponse)
def generate_learning_roadmap(payload: RoadmapGenerationRequest):
    service = GeminiRoadmapService()
    try:
        return service.generate_roadmap(payload.model_dump())
    except Exception as exc:
        # Detailed provider failures are logged by the service; do not disclose them to clients.
        raise HTTPException(status_code=503, detail="Learning roadmap generation is temporarily unavailable.") from exc
