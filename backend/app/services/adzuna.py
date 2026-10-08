"""Official Adzuna HTTPS API. Credentials never appear in responses or logs."""

import logging
import time
import httpx
from app.config.settings import get_settings


class AdzunaError(Exception):
    def __init__(self, code, message, status=503):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


class AdzunaProvider:
    source = "adzuna"
    base_url = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self):
        self.settings = get_settings()

    @property
    def is_configured(self):
        return bool(
            self.settings.adzuna_app_id.strip() and self.settings.adzuna_api_key.strip()
        )

    def fetch_jobs(self, query, location, country, max_days, limit):
        if not self.is_configured:
            raise AdzunaError(
                "provider_not_configured",
                "Set ADZUNA_APP_ID and ADZUNA_API_KEY in backend/.env, then restart the API. No sample jobs are substituted.",
            )
        # httpx INFO request logs include the full query URL (and app_key).
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        results = []
        provider_count = None
        params = {
            "app_id": self.settings.adzuna_app_id,
            "app_key": self.settings.adzuna_api_key,
            "what": query,
            "max_days_old": max_days,
            "sort_by": "date",
            "results_per_page": min(50, limit),
            "content-type": "application/json",
        }
        if location:
            params["where"] = location
        with httpx.Client(
            timeout=self.settings.job_timeout_seconds, follow_redirects=False
        ) as client:
            for page in range(1, (limit + 49) // 50 + 1):
                for attempt in range(self.settings.job_max_retries + 1):
                    try:
                        response = client.get(
                            f"{self.base_url}/{country}/search/{page}",
                            params=params,
                            headers={"Accept": "application/json"},
                        )
                    except httpx.TimeoutException:
                        raise AdzunaError(
                            "provider_timeout",
                            "Adzuna timed out. Please try again.",
                            504,
                        ) from None
                    except httpx.HTTPError:
                        raise AdzunaError(
                            "provider_unavailable",
                            "Unable to contact Adzuna. No fresh matching results were saved.",
                        ) from None
                    if (
                        response.status_code in {429, 500, 502, 503, 504}
                        and attempt < self.settings.job_max_retries
                    ):
                        time.sleep(0.25 * (attempt + 1))
                        continue
                    break
                if response.status_code in {401, 403}:
                    raise AdzunaError(
                        "provider_authentication",
                        "Adzuna rejected the server credentials. Check your app ID/key and account access.",
                        502,
                    )
                if response.status_code == 429:
                    raise AdzunaError(
                        "provider_rate_limited",
                        "Adzuna request quota/rate limit reached. Try again later.",
                        503,
                    )
                if response.status_code != 200:
                    raise AdzunaError(
                        "provider_error",
                        "Adzuna could not complete this search. Check the query and provider account.",
                        502,
                    )
                try:
                    data = response.json()
                    page_results = data["results"]
                    if not isinstance(page_results, list) or not all(
                        isinstance(row, dict) for row in page_results
                    ):
                        raise ValueError()
                    count = data.get("count")
                    if provider_count is None and isinstance(count, (int, float)):
                        provider_count = int(count)
                except (ValueError, KeyError, TypeError):
                    raise AdzunaError(
                        "provider_invalid_response",
                        "Adzuna returned an invalid response; it was not treated as an empty search.",
                        502,
                    ) from None
                results.extend(page_results)
                if len(page_results) < min(50, limit) or len(results) >= limit:
                    break
        return {
            "results": results[:limit],
            "provider_count": provider_count,
            "source": self.source,
        }
