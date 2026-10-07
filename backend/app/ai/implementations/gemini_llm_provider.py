from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional
import httpx

from app.ai.interfaces.llm_provider import LLMExplanationProviderInterface
from app.config.settings import get_settings

log = logging.getLogger(__name__)


class GeminiLLMProvider(LLMExplanationProviderInterface):
    """Generates natural language explanations using Google Gemini API.

    Guarantees that TF-IDF and rule-based score calculations remain 100% deterministic,
    using Gemini purely as an explanation and advice layer.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self.base_url = settings.gemini_base_url

    def explain_match_score(self, match_data: Dict[str, Any]) -> str:
        score = match_data.get("overall_match_score", 0.0)
        matched = match_data.get("matched_skills", [])
        missing = match_data.get("missing_skills", [])

        prompt = (
            f"Explain why candidate has a {score:.1f}% match for this job role. "
            f"Matched skills: {', '.join(matched[:5])}. Missing skills: {', '.join(missing[:5])}. "
            f"Keep explanation clear, professional, and under 3 sentences."
        )

        resp = self._prompt_gemini(prompt)
        if resp:
            return resp
        return f"Your candidate profile achieves a {score:.1f}% match based on strong skill alignment in {', '.join(matched[:3])}."

    def explain_career_readiness(self, readiness_data: Dict[str, Any]) -> str:
        score = readiness_data.get("overall_score", 0.0)
        prompt = (
            f"Provide a 2-sentence summary explanation for a student's Career Readiness Score of {score:.1f}/100, "
            f"encouraging them on how to bridge their current technical and project gaps."
        )
        resp = self._prompt_gemini(prompt)
        if resp:
            return resp
        return f"Your career readiness score of {score:.1f}/100 indicates solid foundation with key growth opportunities in technical skill depth and portfolio projects."

    def explain_recommendations(self, recommendation_data: Dict[str, Any]) -> str:
        target_role = recommendation_data.get("target_role", "Software Engineer")
        prompt = (
            f"Explain in 2 sentences why these recommended projects and certifications will help the candidate reach their target role of {target_role}."
        )
        resp = self._prompt_gemini(prompt)
        if resp:
            return resp
        return f"These tailored recommendations address your highest priority skill gaps to prepare you directly for {target_role} roles."

    def enhance_roadmap_advice(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        target_role = roadmap_data.get("target_role", "Software Engineer")
        prompt = (
            f"Generate 2 strategic career tips for a student pursuing a {target_role} role."
        )
        resp = self._prompt_gemini(prompt)
        advice = resp or f"Focus on building high-impact portfolio projects and mastering core technical requirements for {target_role}."
        roadmap_data["career_advice"] = advice
        return roadmap_data

    def _prompt_gemini(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            return None
        url = f"{self.base_url.rstrip('/')}/models/{self.model}:generateContent?key={self.api_key}"
        try:
            with httpx.Client(timeout=6.0) as client:
                res = client.post(
                    url,
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                )
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
        except Exception as err:
            log.warning(f"Gemini API request failed: {err}")
        return None
