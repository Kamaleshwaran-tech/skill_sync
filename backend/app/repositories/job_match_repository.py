from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.models import JobMatch, MatchDetail, Skill, SkillGap, UserSkill


class JobMatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_match(self, user_id: int, job_id: int, result: dict[str, Any]) -> JobMatch:
        existing = self.db.query(JobMatch).filter(JobMatch.user_id == user_id, JobMatch.job_id == job_id).one_or_none()
        if existing is None:
            match_row = JobMatch(
                user_id=user_id,
                job_id=job_id,
                match_score=result["overall_match_score"],
                matched_skills_count=len(result.get("matched_skills", [])),
                missing_skills_count=len(result.get("missing_skills", [])),
            )
            self.db.add(match_row)
            self.db.commit()
            self.db.refresh(match_row)
        else:
            existing.match_score = result["overall_match_score"]
            existing.matched_skills_count = len(result.get("matched_skills", []))
            existing.missing_skills_count = len(result.get("missing_skills", []))
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            match_row = existing

        detail = MatchDetail(
            job_match_id=match_row.id,
            semantic_similarity=result.get("semantic_similarity"),
            required_skill_coverage=result.get("required_skill_coverage"),
            preferred_skill_coverage=result.get("preferred_skill_coverage"),
            experience_relevance=result.get("experience_relevance"),
            project_relevance=result.get("project_relevance"),
            score_breakdown=result.get("score_breakdown"),
            strengths={"items": result.get("strengths", [])},
            potential_concerns={"items": result.get("potential_concerns", [])},
        )
        self.db.add(detail)
        self.db.commit()

        for skill_name in result.get("missing_skills", []):
            skill = self.db.query(Skill).filter(Skill.name == skill_name).one_or_none()
            if skill is None:
                skill = Skill(name=skill_name, category="technical")
                self.db.add(skill)
                self.db.flush()

            current_proficiency = self.db.query(UserSkill).filter(UserSkill.user_id == user_id, UserSkill.skill_id == skill.id).first()
            current_level = current_proficiency.proficiency if current_proficiency else 0
            gap = SkillGap(
                job_match_id=match_row.id,
                skill_id=skill.id,
                current_proficiency=current_level,
                required_proficiency=3,
                gap_percentage=max(0.0, round(((3 - current_level) / 3.0) * 100.0, 2)) if current_level < 3 else 0.0,
                recommendation=f"Build proficiency in {skill_name} before applying.",
            )
            self.db.add(gap)

        self.db.commit()
        return match_row
