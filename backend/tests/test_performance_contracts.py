"""Correctness/work-count guards, not flaky wall-clock CI thresholds."""

import hashlib
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middleware.compression import WorkspaceCompression
from app.services import job_matching
from scripts.benchmark_matching import BASELINE_SHA256, canonical_output, make_fixture


def test_full_ranking_is_identical_to_pre_optimization_baseline():
    profile, jobs, now = make_fixture()
    ranked = job_matching.rank_jobs(profile, jobs, "in", 30, now=now)
    assert (
        hashlib.sha256(canonical_output(ranked).encode()).hexdigest() == BASELINE_SHA256
    )


def test_resume_prepared_once_per_search_and_never_reused_for_another_profile(
    monkeypatch,
):
    profile, jobs, now = make_fixture()
    original = job_matching.prepare_resume
    calls = []

    def counted(value):
        calls.append(value)
        return original(value)

    monkeypatch.setattr(job_matching, "prepare_resume", counted)
    python_jobs, _ = job_matching.rank_jobs(profile, jobs, "in", 30, now=now)
    assert len(calls) == 1
    other = {"raw_text": "Java developer", "technical_skills": [{"name": "Java"}]}
    java_jobs, _ = job_matching.rank_jobs(other, jobs, "in", 30, now=now)
    assert len(calls) == 2
    assert "Python" in python_jobs[0]["matched_skills"]
    assert "Python" in java_jobs[0]["missing_skills"]
    assert "Python" not in java_jobs[0]["matched_skills"]


def test_selective_gzip_respects_client_encoding_and_excludes_auth_and_files():
    app = FastAPI()
    app.add_middleware(WorkspaceCompression, api_prefix="/custom")

    @app.get("/{path:path}")
    def payload(path):
        return {"text": "synthetic evidence " * 500}

    client = TestClient(app)
    for path in ["/custom/jobs/matches/1", "/custom/resumes/1/analysis"]:
        compressed = client.get(path, headers={"Accept-Encoding": "gzip"})
        plain = client.get(path, headers={"Accept-Encoding": "identity"})
        assert compressed.headers["content-encoding"] == "gzip"
        assert "accept-encoding" in compressed.headers["vary"].lower()
        assert int(compressed.headers["content-length"]) < len(compressed.content)
        assert "content-encoding" not in plain.headers
        assert compressed.json() == plain.json()
    for path in ["/custom/auth/me", "/custom/auth/login", "/custom/resumes/1/file"]:
        assert (
            "content-encoding"
            not in client.get(path, headers={"Accept-Encoding": "gzip"}).headers
        )
