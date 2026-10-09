from __future__ import annotations

from app.services.job_normalization import JobNormalizationService


def test_job_normalization_extracts_skills_and_remote_status():
    normalizer = JobNormalizationService()
    raw = {
        "id": "job-123",
        "title": "Senior Frontend Engineer (React/TypeScript)",
        "company": "Acme Corp",
        "location": "Remote",
        "description": "Need strong React, Node.js and PostgreSQL experience. Must know Git.",
        "created": "2026-08-20T10:30:00Z",
        "redirect_url": "https://example.com/jobs/123",
        "salary": "$120000 - $150000",
        "remote": "remote",
    }
    normalized = normalizer.normalize(raw, "fake_provider")
    assert normalized["title"] == "Senior Frontend Engineer (React/TypeScript)"
    assert normalized["company"] == "Acme Corp"
    assert normalized["remote_status"] == "remote"
    assert normalized["salary_min"] == 120000
    assert "React" in normalized["required_skills"]
    assert "Node.js" in normalized["required_skills"]
    assert "PostgreSQL" in normalized["required_skills"]
    assert normalized["source_name"] == "fake_provider"