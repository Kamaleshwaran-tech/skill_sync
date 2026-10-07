from __future__ import annotations

import json
import logging
import subprocess
from typing import Any
from urllib.parse import urlencode

import httpx

from app.integrations.job_provider import JobProvider

logger = logging.getLogger(__name__)


class AdzunaProvider(JobProvider):
    name = "adzuna"

    def __init__(self, app_id: str, api_key: str, base_url: str, country: str = "in", timeout: float = 25.0):
        self.app_id = app_id
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.country = country or "in"
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        return bool(self.app_id and self.api_key)

    def fetch_jobs(
        self,
        query: str | None = None,
        location: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        if not self.is_configured:
            return []

        clean_query = query.strip() if query and query.strip() else "developer"
        requested_limit = max(1, min(200, int(limit)))
        page_size = min(50, requested_limit)
        params: dict[str, Any] = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "results_per_page": page_size,
            "what": clean_query,
            "content-type": "application/json",
        }
        if location and location.strip() and location.strip().lower() != "all":
            params["where"] = location.strip()

        def fetch_page(page: int) -> list[dict[str, Any]]:
            url = f"{self.base_url}/{self.country}/search/{page}?{urlencode(params)}"
            try:
                cmd = ["curl.exe", "-s", "--max-time", str(int(self.timeout)), url]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0 and res.stdout and res.stdout.strip().startswith("{"):
                    return json.loads(res.stdout).get("results", [])
            except Exception as curl_exc:
                logger.debug("Adzuna curl transport fallback notice: %s", curl_exc)
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.get(url, headers={"Accept": "application/json"})
                    response.raise_for_status()
                    return response.json().get("results", [])
            except Exception as exc:
                logger.warning("Adzuna fetch failed for page %d: %s", page, exc)
                return []

        results: list[dict[str, Any]] = []
        for page in range(1, (requested_limit + page_size - 1) // page_size + 1):
            page_results = fetch_page(page)
            if not page_results:
                break
            results.extend(page_results)
            if len(page_results) < page_size:
                break
        logger.info("Adzuna returned %d live jobs", len(results[:requested_limit]))
        return results[:requested_limit]
