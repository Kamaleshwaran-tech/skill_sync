from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_skill_gap_analysis_service_returns_structured_gap_data():
    payload = {
        "student_skills": [
            {"name": "Python", "proficiency": 4},
            {"name": "React", "proficiency": 4},
            {"name": "Docker", "proficiency": 2},
        ],
        "jobs": [
            {
                "title": "Full Stack Developer",
                "required_skills": ["Python", "React", "Node.js", "PostgreSQL"],
                "preferred_skills": ["Docker", "AWS"],
            }
        ],
        "job_market_demand": {
            "node.js": 0.82,
            "postgresql": 0.74,
            "docker": 0.68,
            "aws": 0.62,
        },
        "prerequisites": {"node.js": ["javascript"], "postgresql": ["sql"]},
    }

    response = client.post("/api/v1/skill-gap/analyze", json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["jobs"]
    first = body["jobs"][0]
    assert first["jobTitle"] == "Full Stack Developer"
    assert "Python" in first["matchedSkills"]
    assert "React" in first["matchedSkills"]
    assert "Node.js" in first["missingSkills"]
    assert first["gaps"]
    gap = first["gaps"][0]
    assert gap["skill"] in {"Node.js", "PostgreSQL", "Docker", "AWS"}
    assert gap["priority"] in {"HIGH", "MEDIUM", "LOW"}
    assert "industryDemand" in gap
    assert "recommendedOrder" in gap
