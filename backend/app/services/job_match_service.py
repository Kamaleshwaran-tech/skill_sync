from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.repositories.job_match_repository import JobMatchRepository
from app.services.semantic_job_matching import SemanticJobMatchingService


class JobMatchService:
    def __init__(self, db: Session, embedder: Any | None = None):
        self.db = db
        self.matcher = SemanticJobMatchingService(embedder=embedder)

    def evaluate_match(self, user_id: int, job_id: int, student_profile: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
        result = self.matcher.calculate(student_profile, job)
        match_record = JobMatchRepository(self.db).save_match(user_id, job_id, result)
        return {
            "job_match": match_record,
            "result": result,
        }

    def calculate_match(self, student_profile: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
        return self.matcher.calculate(student_profile, job)
