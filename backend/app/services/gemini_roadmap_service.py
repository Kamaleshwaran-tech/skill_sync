from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import ValidationError

from app.config.settings import get_settings
from app.schemas.roadmap import LearningRoadmapResponse, RoadmapGenerationRequest
from app.services.learning_roadmap_service import LearningRoadmapPlanningService


class GeminiRoadmapService:
    def __init__(self, client: httpx.Client | None = None):
        self.settings = get_settings()
        self.client = client or httpx.Client(timeout=self.settings.gemini_timeout_seconds)
        self.planner = LearningRoadmapPlanningService()

    def generate_roadmap(self, payload: dict[str, Any]) -> LearningRoadmapResponse:
        context = self.planner.build_context(payload)
        prompt = self._build_prompt(context)

        if not self.settings.gemini_api_key:
            return self._fallback_roadmap(context)

        for attempt in range(max(1, int(self.settings.gemini_max_retries))):
            try:
                raw_response = self._call_gemini(prompt)
                parsed = self._extract_json(raw_response)
                validated = LearningRoadmapResponse.model_validate(parsed)
                return validated
            except (httpx.HTTPError, ValueError, ValidationError, TypeError, json.JSONDecodeError):
                if attempt == max(1, int(self.settings.gemini_max_retries)) - 1:
                    break
                time.sleep(0.5 * (attempt + 1))

        return self._fallback_roadmap(context)

    def _call_gemini(self, prompt: str) -> str:
        url = f"{self.settings.gemini_base_url.rstrip('/')}/models/{self.settings.gemini_model}:generateContent?key={self.settings.gemini_api_key}"
        response = self.client.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            },
        )
        if response.status_code >= 400:
            response.raise_for_status()
        return response.text

    def _extract_json(self, raw_response: str) -> dict[str, Any]:
        data = json.loads(raw_response)
        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError("Gemini response did not include candidates.")
        content = candidates[0].get("content", {})
        parts = content.get("parts") or []
        if not parts:
            raise ValueError("Gemini response did not include text content.")
        text = parts[0].get("text")
        if not text:
            raise ValueError("Gemini response text is empty.")
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("` ")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        return json.loads(cleaned)

    def _build_prompt(self, context: dict[str, Any]) -> str:
        return f"""
You are a career guidance assistant.
Use only the structured input below.
Do not invent personal details about the student.

Structured context:
{json.dumps(context, indent=2)}

Return a valid JSON object matching this schema:
- targetRole: string
- currentSkillLevel: string
- summary: string
- learningSequence: array of objects with order, skill, description, priority, difficulty, estimatedDuration, prerequisites, learningResources (array of objects with keys title, type, url), projectRecommendation, completionStatus
- projectRecommendations: array of strings
- certificationRecommendations: array of strings
- careerAdvice: string
- readinessScore: number
- generatedAt: ISO datetime string

Rules:
- Keep career guidance practical and concise.
- Explain each skill in clear language.
- Prefer the missing skills in the provided recommended order.
- Use only the structured details; do not claim to inspect hidden resume content.
"""

    def _fallback_roadmap(self, context: dict[str, Any]) -> LearningRoadmapResponse:
        missing_skills = context.get("missingSkills", [])
        if not missing_skills:
            missing_skills = ["Core fundamentals"]
        steps = []
        for index, skill in enumerate(missing_skills[:5], start=1):
            steps.append(
                {
                    "order": index,
                    "skill": skill,
                    "description": f"Build mastery in {skill} to improve readiness for {context.get('targetRole', 'the target role')}.",
                    "priority": "HIGH" if index <= 2 else "MEDIUM",
                    "difficulty": "Beginner" if index <= 2 else "Intermediate",
                    "estimatedDuration": "2-4 weeks" if index <= 2 else "4-6 weeks",
                    "prerequisites": context.get("skillDependencies", {}).get(skill, []),
                    "learningResources": [
                        {"title": f"Learn {skill}", "type": "course", "url": None},
                        {"title": f"Project practice for {skill}", "type": "project", "url": None},
                    ],
                    "projectRecommendation": f"Build a focused project using {skill} relevant to {context.get('targetRole', 'the target role')}.",
                    "completionStatus": "not_started",
                }
            )

        return LearningRoadmapResponse(
            targetRole=context.get("targetRole", "Software Engineer"),
            currentSkillLevel="Emerging",
            summary=context.get("deterministicSummary") or "Use a focused learning sequence to close critical role gaps.",
            learningSequence=steps,
            projectRecommendations=[
                f"Create a portfolio project centered on {context.get('targetRole', 'the target role')} and include {', '.join(missing_skills[:2])}."
            ],
            certificationRecommendations=[
                f"Certification aligned to {context.get('targetRole', 'the target role')} fundamentals.",
            ],
            careerAdvice="Focus on the highest-priority missing skills first, then demonstrate them through projects and measurable outcomes.",
            readinessScore=float(context.get("careerReadinessScore", 0.0) or 0.0),
            generatedAt=datetime.now(UTC),
        )
