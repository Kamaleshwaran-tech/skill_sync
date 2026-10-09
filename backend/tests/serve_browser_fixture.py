"""TEST ONLY. Start with python -m tests.serve_browser_fixture.

Uses a separate temporary SQLite DB and intercepts Adzuna HTTP with labelled
synthetic fixtures. Never run as the real application entry point.
"""

import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone

root = Path(tempfile.mkdtemp(prefix="skillsync-browser-fixture-"))
os.environ.update(
    DATABASE_URL="sqlite:///" + str(root / "test.db"),
    RESUME_STORAGE_DIR=str(root / "resumes"),
    JWT_SECRET_KEY="browser-fixture-test-only-secret-never-deploy-123456789",
    ADZUNA_APP_ID="fixture-app-id",
    ADZUNA_API_KEY="fixture-key",
    JOB_MAX_RETRIES="0",
    RATE_LIMIT_PER_MINUTE="600",
)
import httpx
from app.main import app
from app.database.session import Base, engine
from app.services.adzuna import AdzunaProvider

Base.metadata.create_all(engine)
AdzunaProvider.source = "test_fixture"
original_client = httpx.Client


def transport(request):
    query = request.url.params.get("what", "")
    if query == "provider-fail":
        return httpx.Response(401, json={"error": "test provider failure"})
    if query == "no-results":
        return httpx.Response(200, json={"results": [], "count": 0})
    jobs = [
        {
            "id": "fixture-python",
            "title": "TEST FIXTURE — Python Developer",
            "description": "Required: Python, SQL. Preferred: Docker. Build tested database applications.",
            "company": {"display_name": "Synthetic Python Company"},
        },
        {
            "id": "fixture-java",
            "title": "TEST FIXTURE — Java Developer",
            "description": "Required: Java, Spring Boot. Maintain enterprise applications and software.",
            "company": {"display_name": "Synthetic Java Company"},
        },
    ]
    if query == "many-jobs":
        all_jobs = [
            {
                **jobs[0],
                "id": f"fixture-many-{i}",
                "title": f"TEST FIXTURE — Python Developer {i}",
            }
            for i in range(100)
        ]
        page = int(request.url.path.rsplit("/", 1)[1])
        size = int(request.url.params.get("results_per_page", "50"))
        jobs = all_jobs[(page - 1) * size : page * size]
    for job in jobs:
        job.update(
            location={"display_name": "Chennai"},
            created=datetime.now(timezone.utc).isoformat(),
            salary_min=500000,
            salary_max=900000,
            redirect_url="https://www.adzuna.in/jobs/land/ad/" + job["id"],
        )
    return httpx.Response(
        200, json={"results": jobs, "count": 100 if query == "many-jobs" else 2}
    )


httpx.Client = lambda **kwargs: original_client(
    transport=httpx.MockTransport(transport), **kwargs
)
if __name__ == "__main__":
    import uvicorn

    print("TEST FIXTURES ONLY — no live jobs or real credentials", flush=True)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("TEST_PORT", "8001")),
        access_log=False,
    )
