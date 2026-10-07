from __future__ import annotations

from typing import Any

from app.integrations.job_provider import JobProvider
from app.repositories.job_repository import JobRepository
from app.services.job_normalization import JobNormalizationService


class JobIngestionService:
    def __init__(self, providers: list[JobProvider], repo: JobRepository, normalizer: JobNormalizationService):
        self.providers = providers
        self.repo = repo
        self.normalizer = normalizer

    def ingest(self, query: str | None = None, location: str | None = None, limit_per_provider: int = 20) -> dict[str, Any]:
        created = 0
        skipped = 0
        errors: list[str] = []
        seen: set[str] = set()

        for provider in self.providers:
            if not provider.is_configured:
                continue
            try:
                raw_jobs = provider.fetch_jobs(query=query, location=location, limit=limit_per_provider)
                source = self.repo.get_or_create_source(provider.name, api_url=getattr(provider, "base_url", None), provider=provider.name)
                for raw in raw_jobs:
                    normalized = self.normalizer.normalize(raw, provider.name)
                    dedupe_key = f"{provider.name}:{normalized.get('external_id')}"
                    if dedupe_key in seen:
                        skipped += 1
                        continue
                    seen.add(dedupe_key)
                    self.repo.upsert_job(normalized, source.id)
                    created += 1
            except Exception as exc:  # pragma: no cover - resilience path
                errors.append(f"{provider.name}: {exc}")

        return {
            "created": created,
            "skipped": skipped,
            "errors": errors,
        }
