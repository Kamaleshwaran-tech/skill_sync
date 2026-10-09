from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import httpx

from app.ai.interfaces.job_fetcher import JobFetcherInterface, ProcessedJob
from app.utils.skill_taxonomy import normalize_skill, MASTER_SKILLS

log = logging.getLogger(__name__)


class ApiJobFetcher(JobFetcherInterface):
    """Fetches and preprocesses live job descriptions from external job APIs."""

    def __init__(self, adzuna_app_id: str = "", adzuna_app_key: str = "", country: str = ""):
        from app.config.settings import get_settings
        settings = get_settings()
        self.app_id = adzuna_app_id or settings.adzuna_app_id
        self.app_key = adzuna_app_key or settings.adzuna_api_key
        self.country = country or settings.adzuna_country or "gb"
        self.base_url = settings.adzuna_base_url or "https://api.adzuna.com/v1/api/jobs"

    def fetch_jobs(self, query: str, location: Optional[str] = None, limit: int = 10) -> List[ProcessedJob]:
        if not self.app_id or not self.app_key:
            return self._fallback_jobs(query, limit)

        url = f"{self.base_url.rstrip('/')}/{self.country}/search/1"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": limit,
            "what": query,
            "content-type": "application/json",
        }
        if location:
            params["where"] = location

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        return [self.preprocess_job(raw) for raw in results]
        except Exception as err:
            log.warning(f"Adzuna API call failed: {err}. Using fallback provider.")

        return self._fallback_jobs(query, limit)

    def preprocess_job(self, raw_job: Dict[str, Any]) -> ProcessedJob:
        title = str(raw_job.get("title") or "Software Engineer")
        description = str(raw_job.get("description") or title)
        company_info = raw_job.get("company")
        company = company_info.get("display_name") if isinstance(company_info, dict) else str(company_info or "Tech Employer")
        location_info = raw_job.get("location")
        location = ", ".join(location_info.get("display_name", [])) if isinstance(location_info, dict) else str(location_info or "Remote")

        req_skills, pref_skills = self._extract_job_skills(description)

        return ProcessedJob(
            external_id=str(raw_job.get("id") or hash(title + description)),
            title=title,
            company=company,
            location=location,
            description=description,
            required_skills=req_skills,
            preferred_skills=pref_skills,
            experience_required_years=1.0 if "senior" not in title.lower() else 3.0,
            salary_min=raw_job.get("salary_min"),
            salary_max=raw_job.get("salary_max"),
            url=raw_job.get("redirect_url") or raw_job.get("url"),
            source_name="Live Job Provider",
        )

    def _extract_job_skills(self, description: str) -> tuple[List[str], List[str]]:
        import re
        lowered = description.lower()
        sentences = [s.strip() for s in re.split(r"[.\n;]", lowered) if s.strip()]
        req_set = set()
        pref_set = set()

        for skill in MASTER_SKILLS:
            sk_low = skill.lower()
            if sk_low in lowered:
                is_preferred = False
                for sentence in sentences:
                    if sk_low in sentence:
                        if any(kw in sentence for kw in ["preferred", "nice to have", "plus", "optional"]):
                            is_preferred = True
                            break
                if is_preferred:
                    pref_set.add(skill)
                else:
                    req_set.add(skill)

        if not req_set and not pref_set:
            req_set = {"Python", "Git"}

        return sorted(list(req_set)), sorted(list(pref_set))

    def _fallback_jobs(self, query: str, limit: int) -> List[ProcessedJob]:
        return [
            ProcessedJob(
                external_id=f"sample-{i+1}",
                title=f"{query.capitalize()} Specialist",
                company="SkillSync Partner Network",
                location="Remote",
                description=f"Active benchmark role seeking expertise in {query}, React, Python, PostgreSQL, and Docker.",
                required_skills=["Python", "React", "PostgreSQL", "Git"],
                preferred_skills=["Docker", "AWS"],
                experience_required_years=2.0,
                source_name="SkillSync Benchmark Ingestion",
            )
            for i in range(min(limit, 3))
        ]
