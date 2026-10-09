from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Iterable

from app.services.job_skill_extraction import JobSkillExtractionService
from app.utils.skill_taxonomy import MASTER_SKILLS, normalize_skill


class JobNormalizationService:
    def __init__(self, skill_extractor: JobSkillExtractionService | None = None):
        self.skill_extractor = skill_extractor or JobSkillExtractionService()

    def normalize(self, raw_job: dict[str, Any], source_name: str) -> dict[str, Any]:
        title = self._as_text(raw_job.get("title") or raw_job.get("job_title") or "")
        company = self._as_text(raw_job.get("company") or raw_job.get("company_name") or raw_job.get("employer") or "")
        description = self._as_text(raw_job.get("description") or raw_job.get("summary") or raw_job.get("snippet") or "")
        location = self._as_text(raw_job.get("location") or raw_job.get("city") or raw_job.get("place") or raw_job.get("address") or "")
        remote_status = self._normalize_remote(raw_job.get("remote") or raw_job.get("work_from_home") or raw_job.get("remote_status") or description)
        salary_min, salary_max = self._normalize_salary_bounds(raw_job)
        experience_level = self._normalize_experience(raw_job.get("experience_level") or raw_job.get("experience") or raw_job.get("experience_required") or "")
        posted_date = self._normalize_date(raw_job.get("created") or raw_job.get("posted_date") or raw_job.get("published") or raw_job.get("date"))
        application_url = self._as_text(raw_job.get("redirect_url") or raw_job.get("url") or raw_job.get("application_url") or "")
        external_id = self._as_text(raw_job.get("id") or raw_job.get("external_id") or raw_job.get("job_id") or f"{source_name}:{title}:{company}")

        extracted = self.skill_extractor.extract(title, description)
        required_skill_names = extracted.get("required", [])
        preferred_skill_names = extracted.get("preferred", [])
        soft_skill_names = extracted.get("soft_skills", [])

        return {
            "external_id": external_id,
            "title": title or "Untitled Role",
            "company": company or "Unknown Company",
            "description": description,
            "location": location or "Remote",
            "remote_status": remote_status,
            "job_type": self._as_text(raw_job.get("contract_type") or raw_job.get("job_type") or raw_job.get("employment_type") or "") or "unknown",
            "salary_min": salary_min,
            "salary_max": salary_max,
            "experience_level": experience_level,
            "required_skills": required_skill_names,
            "preferred_skills": preferred_skill_names,
            "soft_skills": soft_skill_names,
            "posted_date": posted_date,
            "application_url": application_url,
            "source_name": source_name,
            "is_active": True,
            "expires_at": self._normalize_expiration(raw_job),
        }

    def _as_text(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (list, tuple)):
            return " ".join(str(v) for v in value if v)
        if isinstance(value, dict):
            return self._as_text(
                value.get("display_name")
                or value.get("display")
                or value.get("name")
                or value.get("label")
                or value.get("text")
            )
        return str(value).strip()

    def _normalize_salary_bounds(self, raw_job: dict[str, Any]) -> tuple[int | None, int | None]:
        """Preserve provider-supplied bounds instead of reducing them to one salary."""
        minimum = raw_job.get("salary_min")
        if minimum is None:
            minimum = raw_job.get("salaryMinimum")
        maximum = raw_job.get("salary_max")
        if maximum is None:
            maximum = raw_job.get("salaryMaximum")
        if minimum is not None or maximum is not None:
            low = self._normalize_salary(minimum)[0] if minimum is not None else None
            high = self._normalize_salary(maximum)[1] if maximum is not None else None
            return low, high
        return self._normalize_salary(raw_job.get("salary") or raw_job.get("salary_range"))

    def _normalize_remote(self, value: Any) -> str:
        text = self._as_text(value).lower()
        if not text:
            return "unknown"
        if "remote" in text or "hybrid" in text:
            return "remote" if "remote" in text else "hybrid"
        if "onsite" in text or "in-office" in text or "office" in text:
            return "onsite"
        return "unknown"

    def _normalize_salary(self, value: Any) -> tuple[int | None, int | None]:
        if value is None:
            return (None, None)
        if isinstance(value, dict):
            lower = value.get("min") or value.get("salary_min") or value.get("minimum")
            upper = value.get("max") or value.get("salary_max") or value.get("maximum")
            return self._normalize_salary({"min": lower, "max": upper})
        if isinstance(value, (int, float)):
            return (int(value), int(value))
        text = self._as_text(value)
        numbers = re.findall(r"\$?(\d[\d,\.]*)", text)
        if not numbers:
            return (None, None)
        cleaned = [int(float(n.replace(",", ""))) for n in numbers[:2]]
        if len(cleaned) == 1:
            return (cleaned[0], cleaned[0])
        return (cleaned[0], cleaned[1])

    def _normalize_experience(self, value: Any) -> str:
        text = self._as_text(value).lower()
        if not text:
            return "unknown"
        if any(v in text for v in ("senior", "lead")):
            return "senior"
        if any(v in text for v in ("mid", "intermediate")):
            return "mid"
        if any(v in text for v in ("junior", "entry")):
            return "junior"
        return text

    def _normalize_date(self, value: Any):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
            except ValueError:
                return None
        return None

    def _normalize_expiration(self, raw_job: dict[str, Any]):
        value = raw_job.get("expires_at") or raw_job.get("expiry") or raw_job.get("deadline")
        if not value:
            return None
        return self._normalize_date(value)

    def _extract_required_skills(self, raw_job: dict[str, Any], title: str, description: str) -> list[str]:
        skill_names: set[str] = set()
        raw_tokens: list[str] = []

        for key in ("required_skills", "skills", "keywords", "skill_tags"):
            val = raw_job.get(key)
            if isinstance(val, list):
                raw_tokens.extend(str(v) for v in val)
            elif isinstance(val, str):
                raw_tokens.extend([val])

        text_blob = f"{title} {description} {' '.join(raw_tokens)}"
        for candidate in re.split(r"[,;|/\n]+", text_blob):
            normalized = normalize_skill(candidate)
            if normalized:
                skill_names.add(normalized)

        # match canonical skill names from the taxonomy directly in text
        for skill in MASTER_SKILLS:
            if skill.lower() in text_blob.lower():
                skill_names.add(skill)

        return sorted(skill_names)
