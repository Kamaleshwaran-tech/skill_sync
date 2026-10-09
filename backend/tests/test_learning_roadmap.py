from __future__ import annotations

import json

import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.services.gemini_roadmap_service import GeminiRoadmapService


client = TestClient(app)


def test_learning_roadmap_planner_builds_structured_context():
    payload = {
        "currentSkills": ["Python", "React"],
        "targetRole": "Full Stack Developer",
        "missingSkills": ["Node.js", "PostgreSQL", "Docker"],
        "skillPriorities": {"Node.js": "HIGH", "PostgreSQL": "HIGH", "Docker": "MEDIUM"},
        "skillDependencies": {"Node.js": ["JavaScript"], "PostgreSQL": ["SQL"]},
        "industryDemand": {"Node.js": 0.82, "PostgreSQL": 0.74, "Docker": 0.68},
        "careerReadinessScore": 84,
    }

    service = GeminiRoadmapService()
    context = service.planner.build_context(payload)
    assert context["targetRole"] == "Full Stack Developer"
    assert context["missingSkills"][0] == "Node.js"
    assert context["skillDependencies"]["Node.js"] == ["JavaScript"]
    assert context["careerReadinessScore"] == 84


def test_gemini_roadmap_service_falls_back_on_malformed_response():
    class FakeClient:
        def post(self, *args, **kwargs):
            return httpx.Response(200, text="{not-valid-json}")

    service = GeminiRoadmapService(client=FakeClient())
    service.settings.gemini_api_key = "fake-key"
    result = service.generate_roadmap(
        {
            "currentSkills": ["Python"],
            "targetRole": "Backend Developer",
            "missingSkills": ["Docker", "PostgreSQL"],
            "skillPriorities": {"Docker": "MEDIUM", "PostgreSQL": "HIGH"},
            "skillDependencies": {"PostgreSQL": ["SQL"]},
            "industryDemand": {"Docker": 0.7, "PostgreSQL": 0.8},
            "careerReadinessScore": 78,
        }
    )

    assert result.targetRole == "Backend Developer"
    assert result.learningSequence
    assert result.summary


def test_learning_roadmap_route_returns_valid_response():
    response = client.post(
        "/api/v1/roadmaps/generate",
        json={
            "currentSkills": ["Python", "React"],
            "targetRole": "Full Stack Developer",
            "missingSkills": ["Node.js", "PostgreSQL"],
            "skillPriorities": {"Node.js": "HIGH", "PostgreSQL": "HIGH"},
            "skillDependencies": {"Node.js": ["JavaScript"], "PostgreSQL": ["SQL"]},
            "industryDemand": {"Node.js": 0.82, "PostgreSQL": 0.74},
            "careerReadinessScore": 82,
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["targetRole"] == "Full Stack Developer"
    assert payload["learningSequence"][0]["skill"] in {"Node.js", "PostgreSQL"}
    assert payload["projectRecommendations"]
