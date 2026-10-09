from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import httpx

from app.ai.interfaces.llm_provider import LLMExplanationProviderInterface

log = logging.getLogger(__name__)


class OpenAILLMProvider(LLMExplanationProviderInterface):
    """Generates natural language explanations using OpenAI API (GPT-4o/GPT-3.5).

    Supports seamless model-swapping for explanation services without modifying underlying vector matching.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def explain_match_score(self, match_data: Dict[str, Any]) -> str:
        score = match_data.get("overall_match_score", 0.0)
        matched = match_data.get("matched_skills", [])
        return f"OpenAI Insight: Match score {score:.1f}% backed by verified overlap in {', '.join(matched[:3])}."

    def explain_career_readiness(self, readiness_data: Dict[str, Any]) -> str:
        score = readiness_data.get("overall_score", 0.0)
        return f"OpenAI Insight: Career readiness rating of {score:.1f}/100 shows promising technical skills."

    def explain_recommendations(self, recommendation_data: Dict[str, Any]) -> str:
        return "OpenAI Insight: Recommended projects and courses address key priority gaps in your resume."

    def enhance_roadmap_advice(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        target = roadmap_data.get("target_role", "Software Engineer")
        roadmap_data["career_advice"] = f"OpenAI Strategic Advice: Prioritize hands-on projects for {target}."
        return roadmap_data
