from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.models import Job, JobSkill, JobSource, Skill


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_source(self, provider_name: str, api_url: str | None = None, provider: str | None = None) -> JobSource:
        source = self.db.query(JobSource).filter(JobSource.name == provider_name).one_or_none()
        if source is None:
            source = JobSource(name=provider_name, provider=provider or provider_name, api_url=api_url)
            self.db.add(source)
            self.db.commit()
            self.db.refresh(source)
        return source

    def upsert_job(self, normalized: dict[str, Any], source_id: int) -> Job:
        external_id = normalized.get("external_id")
        job = self.db.query(Job).filter(Job.source_id == source_id, Job.external_id == external_id).one_or_none()

        if job is None:
            job = Job(
                source_id=source_id,
                external_id=external_id,
                title=normalized["title"],
                company=normalized["company"],
                location=normalized["location"],
                job_type=normalized.get("job_type") or "unknown",
                salary_min=normalized.get("salary_min"),
                salary_max=normalized.get("salary_max"),
                description=normalized.get("description"),
                posted_date=normalized.get("posted_date"),
                url=normalized.get("application_url"),
                expires_at=normalized.get("expires_at"),
                is_active=normalized.get("is_active", True),
            )
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
        else:
            job.title = normalized["title"]
            job.company = normalized["company"]
            job.location = normalized["location"]
            job.job_type = normalized.get("job_type") or job.job_type or "unknown"
            job.salary_min = normalized.get("salary_min")
            job.salary_max = normalized.get("salary_max")
            job.description = normalized.get("description")
            job.posted_date = normalized.get("posted_date")
            job.url = normalized.get("application_url")
            job.expires_at = normalized.get("expires_at")
            job.is_active = normalized.get("is_active", True)
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)

        self.save_job_skills(job.id, normalized.get("required_skills", []), "required")
        self.save_job_skills(job.id, normalized.get("preferred_skills", []), "preferred")
        self.save_job_skills(job.id, normalized.get("soft_skills", []), "soft")
        return job

    def save_job_skills(self, job_id: int, skill_names: list[str], skill_type: str) -> None:
        for name in skill_names:
            skill = self.db.query(Skill).filter(Skill.name == name).one_or_none()
            if skill is None:
                skill = Skill(name=name, category="technical")
                self.db.add(skill)
                self.db.flush()
            association = self.db.query(JobSkill).filter(JobSkill.job_id == job_id, JobSkill.skill_id == skill.id).one_or_none()
            if association is None:
                self.db.add(JobSkill(job_id=job_id, skill_id=skill.id, skill_type=skill_type, importance=1.0, required_proficiency=3))
            else:
                association.skill_type = skill_type
                association.importance = association.importance or 1.0
        self.db.commit()

    def list_jobs(
        self,
        search: str | None = None,
        location: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Job]:
        query = self.db.query(Job).filter(
            Job.is_active.is_(True),
            or_(Job.expires_at.is_(None), Job.expires_at >= datetime.now(timezone.utc).date()),
        )
        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(or_(Job.title.ilike(term), Job.company.ilike(term), Job.description.ilike(term)))
        if location and location.strip():
            query = query.filter(Job.location.ilike(f"%{location.strip()}%"))
        return query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()

    def needs_refresh(self, max_age_minutes: int) -> bool:
        latest = self.db.query(Job.updated_at).filter(Job.is_active.is_(True)).order_by(Job.updated_at.desc()).first()
        if not latest or not latest[0]:
            return True
        updated_at = latest[0]
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        return updated_at < datetime.now(timezone.utc) - timedelta(minutes=max(1, max_age_minutes))
