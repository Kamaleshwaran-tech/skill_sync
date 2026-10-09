from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_career_readiness_route_returns_weighted_scores_with_explanations():
    payload = {
        "student_skills": [
            {"name": "Python", "proficiency": 4},
            {"name": "React", "proficiency": 4},
            {"name": "Docker", "proficiency": 3},
            {"name": "PostgreSQL", "proficiency": 3},
        ],
        "required_skills": ["Python", "React", "Node.js", "PostgreSQL", "Docker"],
        "project_count": 3,
        "target_project_count": 4,
        "experience_years": 2,
        "target_experience_years": 3,
        "resume_sections": {
            "summary": True,
            "skills": True,
            "experience": True,
            "education": True,
            "projects": True,
            "certifications": False,
        },
        "industry_demand": {
            "python": 0.9,
            "react": 0.8,
            "docker": 0.7,
            "postgresql": 0.75,
        },
        "target_role_match_score": 84,
    }

    response = client.post("/api/v1/career-readiness/score", json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    assert 0 <= body["overallScore"] <= 100
    assert body["technicalScore"]["score"] >= 0
    assert body["technicalScore"]["reason"]
    assert body["overallReason"]
    assert body["interpretation"]
    assert body["weights"]["technical"] > 0
