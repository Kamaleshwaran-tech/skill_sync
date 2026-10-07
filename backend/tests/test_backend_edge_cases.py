from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.main import app
from app.models.models import User
from app.services.gemini_roadmap_service import GeminiRoadmapService
from app.integrations.providers.adzuna import AdzunaProvider
from app.services.job_ingestion_service import JobIngestionService
from app.services.job_normalization import JobNormalizationService
from app.services.resume_parser import ResumeParser
from app.services.semantic_job_matching import SemanticJobMatchingService
from app.utils.security import create_access_token, decode_token
from app.utils.skill_taxonomy import normalize_skill

client = TestClient(app)


def test_resume_parser_handles_empty_resume_and_unknown_skills():
    parser = ResumeParser()
    with pytest.raises(ValueError, match="too little readable text"):
        parser.extract_structured("   \n\n  ")
    assert normalize_skill("QuantumFluxMysterySkill") is None


def test_invalid_pdf_fails_gracefully(tmp_path):
    bad_pdf = tmp_path / "bad.pdf"
    bad_pdf.write_bytes(b"not a real pdf")
    parser = ResumeParser()

    with pytest.raises((RuntimeError, ValueError, FileNotFoundError, OSError)):
        parser.extract_text_from_pdf(str(bad_pdf))


def test_job_ingestion_deduplicates_jobs_and_handles_provider_errors():
    job = {
        "id": "job-1",
        "title": "Full Stack Developer",
        "company": "Example Labs",
        "location": "Remote",
        "description": "Experience with React, Node.js, PostgreSQL and Docker.",
        "remote": "remote",
        "created": "2026-08-20T12:00:00Z",
        "redirect_url": "https://example.com/jobs/job-1",
    }

    class FakeProvider:
        name = "fake_provider"
        is_configured = True
        base_url = "https://example.com/jobs"

        def fetch_jobs(self, query=None, location=None, limit=20):
            return [job, job]

    class BrokenProvider:
        name = "broken_provider"
        is_configured = True
        base_url = "https://example.com/broken"

        def fetch_jobs(self, query=None, location=None, limit=20):
            raise RuntimeError("Provider unavailable")

    repo = SimpleNamespace(
        get_or_create_source=lambda *args, **kwargs: SimpleNamespace(id=1),
        upsert_job=lambda *args, **kwargs: None,
    )

    service = JobIngestionService([FakeProvider(), BrokenProvider()], repo, JobNormalizationService())
    result = service.ingest(query="full stack", limit_per_provider=10)

    assert result["created"] == 1
    assert result["skipped"] == 1
    assert any("broken_provider" in error for error in result["errors"])


def test_adzuna_provider_paginates_up_to_requested_limit(monkeypatch):
    calls = []

    def fake_run(command, capture_output, text):
        calls.append(command[-1])
        page = 1 if "/search/1?" in command[-1] else 2
        jobs = [{"id": f"{page}-{index}"} for index in range(50)]
        return SimpleNamespace(returncode=0, stdout=json.dumps({"results": jobs}))

    monkeypatch.setattr("app.integrations.providers.adzuna.subprocess.run", fake_run)
    provider = AdzunaProvider("id", "key", "https://example.test/jobs", country="in")

    jobs = provider.fetch_jobs(query="python", limit=75)

    assert len(jobs) == 75
    assert len(calls) == 2


def test_semantic_job_matching_handles_no_matching_jobs():
    service = SemanticJobMatchingService()
    result = service.calculate(
        {"skills": ["Python"], "resume_text": "Python developer", "experience_years": 1},
        {"required_skills": ["AWS", "Kubernetes"], "preferred_skills": ["Docker"], "description": "Need AWS and Kubernetes experience", "experience_required_years": 3},
    )

    assert result["missing_skills"]
    assert result["overall_match_score"] < 40
    assert "AWS" in result["missing_skills"]


def test_gemini_roadmap_service_falls_back_when_api_is_unavailable():
    service = GeminiRoadmapService()
    service.settings.gemini_api_key = ""
    result = service.generate_roadmap({
        "currentSkills": ["Python"],
        "targetRole": "Backend Developer",
        "missingSkills": ["Docker", "AWS"],
        "skillPriorities": {"Docker": "HIGH", "AWS": "MEDIUM"},
        "skillDependencies": {"Docker": ["Linux"], "AWS": ["Cloud fundamentals"]},
        "industryDemand": {"Docker": 0.75, "AWS": 0.81},
        "careerReadinessScore": 74,
    })

    assert result.targetRole == "Backend Developer"
    assert result.learningSequence
    assert result.projectRecommendations

    broken = GeminiRoadmapService(client=httpx.Client())
    broken.settings.gemini_api_key = "fake-key"
    broken._call_gemini = lambda *args, **kwargs: (_ for _ in ()).throw(httpx.HTTPError("offline"))
    fallback = broken.generate_roadmap({
        "currentSkills": ["Python"],
        "targetRole": "Data Engineer",
        "missingSkills": ["SQL"],
        "skillPriorities": {"SQL": "HIGH"},
        "skillDependencies": {"SQL": ["Databases"]},
        "industryDemand": {"SQL": 0.8},
        "careerReadinessScore": 80,
    })
    assert fallback.targetRole == "Data Engineer"


def test_expired_jwt_is_rejected():
    expired_token, _ = create_access_token(123, expires_delta=timedelta(minutes=-10))

    with pytest.raises(Exception):
        decode_token(expired_token)


def test_database_unavailable_is_detected():
    from app.database import session as session_module

    original = session_module.engine.connect

    def boom(*args, **kwargs):
        raise RuntimeError("database unavailable")

    session_module.engine.connect = boom
    try:
        healthy, message = session_module.check_database_connection()
        assert healthy is False
        assert "Database connection failed" in message
    finally:
        session_module.engine.connect = original


def test_sqlalchemy_database_persistence_works():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        email = "db-test@example.com"
        session.query(User).filter(User.email == email).delete()
        session.commit()

        user = User(email=email, hashed_password="hashed", full_name="DB Test User")
        session.add(user)
        session.commit()

        saved = session.query(User).filter(User.email == email).one()
        assert saved.full_name == "DB Test User"
        assert saved.email == email
    finally:
        session.query(User).filter(User.email == email).delete()
        session.commit()
        session.close()


def test_api_authentication_error_and_expired_session_are_handled():
    register = client.post("/api/v1/auth/register", json={"email": "edge@example.com", "password": "s3cureP@ssword", "full_name": "Edge User"})
    assert register.status_code == 200

    login = client.post("/api/v1/auth/login", json={"email": "edge@example.com", "password": "s3cureP@ssword"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    bad = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert bad.status_code == 401

    expired_token, _ = create_access_token(999999, expires_delta=timedelta(minutes=-1))
    expired_response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert expired_response.status_code == 401

    valid = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert valid.status_code == 200
