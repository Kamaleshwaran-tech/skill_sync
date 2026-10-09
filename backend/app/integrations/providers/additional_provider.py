from __future__ import annotations

import logging
from typing import Any

import httpx

from app.integrations.job_provider import JobProvider

logger = logging.getLogger(__name__)


class AdditionalProvider(JobProvider):
    name = "additional"

    def __init__(self, base_url: str, api_key: str | None = None, timeout: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url)

    def fetch_jobs(
        self,
        query: str | None = None,
        location: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        if not self.is_configured:
            return []

        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        params: dict[str, Any] = {"limit": max(1, min(50, int(limit)))}
        if query:
            params["query"] = query
        if location:
            params["location"] = location

        try:
            response = httpx.get(self.base_url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, list):
                return payload
            if isinstance(payload, dict):
                for key in ("results", "jobs", "data"):
                    if isinstance(payload.get(key), list):
                        return payload[key]
            return []
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Additional provider fetch failed: %s", exc)
            return []
