from __future__ import annotations

from typing import Any

from app.integrations.job_provider import JobProvider
from app.repositories.job_repository import JobRepository
from app.services.job_normalization import JobNormalizationService


class JobService:
    def __init__(self, providers: list[JobProvider], repo: JobRepository, normalizer: JobNormalizationService):
        self.providers = providers
        self.repo = repo
        self.normalizer = normalizer

    def fetch_jobs(self, query: str | None = None, location: str | None = None, limit_per_provider: int = 20) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for provider in self.providers:
            if not provider.is_configured:
                continue
            try:
                raw_jobs = provider.fetch_jobs(query=query, location=location, limit=limit_per_provider)
                for raw in raw_jobs:
                    results.append(self.normalizer.normalize(raw, provider.name))
            except Exception:
                continue
        return results
