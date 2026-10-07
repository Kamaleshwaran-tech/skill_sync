from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import (
    CareerReadiness,
    Job,
    JobMatch,
    JobSkill,
    LearningRoadmap,
    Recommendation,
    Resume,
    ResumeAnalysis,
    RoadmapItem,
    Skill,
    SkillGap,
    UserSkill,
    UserPreference,
)
from app.services.semantic_job_matching import SemanticJobMatchingService


class DashboardService:
    def build_dashboard(self, db: Session, user: Any) -> dict[str, Any]:
        # Matching is deterministic and local. Build it here so the dashboard
        # works immediately after resume analysis instead of waiting for the
        # user to visit the separate Job Matches page first.
        live_matches = self._calculate_live_matches(db, user.id)
        profile = self._build_profile(db, user)
        readiness = self._build_readiness(db, user.id, live_matches)
        career_matches = self._build_career_matches(db, user.id, live_matches)
        skill_overview = self._build_skill_overview(db, user.id, live_matches)
        recommended_jobs = self._build_recommended_jobs(db, user.id, live_matches)
        skill_demand = self._build_skill_demand(db)
        learning_progress = self._build_learning_progress(db, user.id)
        recommended_projects = self._build_recommended_projects(db, user.id)
        certifications = self._build_certifications(db, user.id)
        recent_activity = self._build_recent_activity(db, user.id)

        resume_score = self._coerce_int(self._latest_resume_score(db, user.id), 0)
        career_readiness_score = self._coerce_int(readiness["overall"], resume_score)

        payload = {
            "profile": profile,
            "readiness": readiness,
            "careerMatches": career_matches,
            "skillOverview": skill_overview,
            "recommendedJobs": recommended_jobs,
            "skillDemand": skill_demand,
            "learningProgress": learning_progress,
            "recommendedProjects": recommended_projects,
            "certifications": certifications,
            "recentActivity": recent_activity,
            "resumeScore": resume_score,
            "careerReadinessScore": career_readiness_score,
        }
        return payload

    def _build_profile(self, db: Session, user: Any) -> dict[str, str]:
        name = user.full_name or user.email.split("@")[0].title()
        role = "Student" if not getattr(user, "role", None) else str(user.role).replace("_", " ").title()
        preferences = db.query(UserPreference).filter(UserPreference.user_id == user.id).one_or_none()
        values = (preferences.preferences if preferences else {}) or {}
        target_roles = values.get("targetRoles") or []
        return {
            "name": name,
            "role": role,
            "lastUpdated": "Updated today",
            "focus": target_roles[0] if target_roles else "Add a target role in your profile",
        }

    def _build_readiness(self, db: Session, user_id: int, live_matches: list[tuple[Job, dict[str, Any]]]) -> dict[str, Any]:
        latest = (
            db.query(CareerReadiness)
            .filter(CareerReadiness.user_id == user_id)
            .order_by(CareerReadiness.updated_at.desc())
            .first()
        )

        if latest:
            overall = self._coerce_int(latest.overall_score, 0)
            metrics = [
                {"label": "Technical Skills", "value": self._coerce_int(latest.technical_score, 0), "trend": ""},
                {"label": "Industry Match", "value": self._coerce_int(latest.industry_score, 0), "trend": ""},
                {"label": "Resume Quality", "value": self._coerce_int(latest.resume_score, 0), "trend": ""},
                {"label": "Project Strength", "value": self._coerce_int(latest.project_score, 0), "trend": ""},
            ]
            return {"overall": overall, "metrics": metrics}

        skill_count = db.query(func.count(UserSkill.id)).filter(UserSkill.user_id == user_id).scalar() or 0
        latest_analysis = (
            db.query(ResumeAnalysis)
            .join(Resume, Resume.id == ResumeAnalysis.resume_id)
            .filter(Resume.user_id == user_id)
            .order_by(ResumeAnalysis.created_at.desc())
            .first()
        )
        resume_score = self._coerce_int((latest_analysis.confidence * 100) if latest_analysis and latest_analysis.confidence is not None else 0, 0)
        technical_score = min(round(skill_count * 3.5 + 25), 95) if skill_count else 0
        industry_score = self._coerce_int(
            sum(result["overall_match_score"] for _, result in live_matches) / len(live_matches), 0
        ) if live_matches else 0
        profile_data = latest_analysis.profile if latest_analysis and latest_analysis.profile else {}
        projects_list = profile_data.get("projects") or []
        project_score = min(len(projects_list) * 20 + 45, 90) if projects_list else (70 if resume_score else 0)

        overall = round(
            technical_score * 0.30 +
            resume_score * 0.25 +
            industry_score * 0.25 +
            project_score * 0.20
        ) if (skill_count or resume_score or industry_score) else 0

        return {"overall": overall, "metrics": [
            {"label": "Technical Skills", "value": technical_score, "trend": ""},
            {"label": "Industry Match", "value": industry_score, "trend": ""},
            {"label": "Resume Quality", "value": resume_score, "trend": ""},
            {"label": "Project Strength", "value": project_score, "trend": ""},
        ]}

    def _build_career_matches(self, db: Session, user_id: int, live_matches: list[tuple[Job, dict[str, Any]]]) -> list[dict[str, Any]]:
        if live_matches:
            return [
                {
                    "role": job.title,
                    "match": self._coerce_int(result["overall_match_score"], 0),
                    "skillGapCount": len(result["missing_skills"]),
                    "focus": self._build_focus_from_job(job.title),
                }
                for job, result in sorted(live_matches, key=lambda item: item[1]["overall_match_score"], reverse=True)[:4]
            ]
        matches = (
            db.query(JobMatch, Job)
            .join(Job, Job.id == JobMatch.job_id)
            .filter(JobMatch.user_id == user_id)
            .order_by(JobMatch.updated_at.desc())
            .limit(4)
            .all()
        )

        items = []
        for match, job in matches:
            skill_gap_count = int(match.missing_skills_count or 0)
            focus = self._build_focus_from_job(job.title)
            items.append({
                "role": job.title,
                "match": self._coerce_int(match.match_score, 85),
                "skillGapCount": skill_gap_count,
                "focus": focus,
            })
        if items:
            return items
        return []

    def _build_skill_overview(self, db: Session, user_id: int, live_matches: list[tuple[Job, dict[str, Any]]]) -> dict[str, list[str]]:
        user_skill_names = [
            skill.name for skill in db.query(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .filter(UserSkill.user_id == user_id)
            .order_by(Skill.name.asc())
            .limit(10)
            .all()
        ]

        missing_skills = []
        missing_skill_rows = (
            db.query(Skill.name)
            .join(SkillGap, SkillGap.skill_id == Skill.id)
            .join(JobMatch, JobMatch.id == SkillGap.job_match_id)
            .filter(JobMatch.user_id == user_id)
            .order_by(Skill.name.asc())
            .limit(10)
            .all()
        )
        if missing_skill_rows:
            missing_skills.extend(str(name) for (name,) in missing_skill_rows)
        for _, result in sorted(live_matches, key=lambda item: item[1]["overall_match_score"], reverse=True):
            missing_skills.extend(result["missing_skills"])
        missing_skills = list(dict.fromkeys(missing_skills))
        if not user_skill_names and not missing_skills:
            return {"current": [], "strong": [], "developing": [], "missing": []}

        current = user_skill_names[:5]
        missing = missing_skills[:4]
        strong = []
        developing = []
        return {"current": current, "strong": strong, "developing": developing, "missing": missing}

    def _build_recommended_jobs(self, db: Session, user_id: int, live_matches: list[tuple[Job, dict[str, Any]]]) -> list[dict[str, Any]]:
        if live_matches:
            return [
                {
                    "title": job.title,
                    "company": job.company or "Unknown Company",
                    "location": job.location or "Remote",
                    "match": self._coerce_int(result["overall_match_score"], 0),
                    "requiredSkills": result["matched_skills"] + result["missing_skills"],
                }
                for job, result in sorted(live_matches, key=lambda item: item[1]["overall_match_score"], reverse=True)[:3]
            ]
        matches = (
            db.query(JobMatch, Job)
            .join(Job, Job.id == JobMatch.job_id)
            .filter(JobMatch.user_id == user_id)
            .order_by(JobMatch.match_score.desc(), JobMatch.updated_at.desc())
            .limit(3)
            .all()
        )
        items = []
        for match, job in matches:
            skills = [
                skill.name for skill in db.query(Skill.name)
                .join(JobSkill, JobSkill.skill_id == Skill.id)
                .filter(JobSkill.job_id == job.id)
                .order_by(Skill.name.asc())
                .limit(4)
                .all()
            ]
            items.append({
                "title": job.title,
                "company": job.company or "Unknown Company",
                "location": job.location or "Remote",
                "match": self._coerce_int(match.match_score, 90),
                "requiredSkills": skills or ["React", "JavaScript", "SQL"],
            })
        if items:
            return items
        return []

    def _calculate_live_matches(self, db: Session, user_id: int) -> list[tuple[Job, dict[str, Any]]]:
        """Return fresh local scores without a Gemini or external-network call."""
        resume = (
            db.query(Resume)
            .filter(Resume.user_id == user_id, Resume.status == "COMPLETED")
            .order_by(Resume.is_active.desc(), Resume.uploaded_at.desc())
            .first()
        )
        if not resume:
            return []

        user_skills = [
            name for (name,) in db.query(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .filter(UserSkill.user_id == user_id)
            .all()
        ]
        jobs = db.query(Job).filter(Job.is_active.is_(True)).order_by(Job.created_at.desc()).limit(20).all()
        matcher = SemanticJobMatchingService()
        results: list[tuple[Job, dict[str, Any]]] = []
        for job in jobs:
            required = [item.skill.name for item in job.required_skills if item.skill and item.skill_type == "required"]
            preferred = [item.skill.name for item in job.required_skills if item.skill and item.skill_type == "preferred"]
            result = matcher.calculate(
                {"skills": user_skills, "resume_text": resume.parsed_text or " ".join(user_skills)},
                {"description": job.description or "", "required_skills": required, "preferred_skills": preferred},
            )
            results.append((job, result))
        return results

    def _build_skill_demand(self, db: Session) -> list[dict[str, int]]:
        rows = (
            db.query(Skill.name, func.count(JobSkill.id).label("demand_count"))
            .join(JobSkill, JobSkill.skill_id == Skill.id)
            .group_by(Skill.name)
            .order_by(func.count(JobSkill.id).desc())
            .limit(6)
            .all()
        )
        if rows:
            max_count = max((count for _, count in rows), default=1)
            return [{"skill": name, "demand": int(round((count / max_count) * 100))} for name, count in rows]
        return []

    def _build_learning_progress(self, db: Session, user_id: int) -> dict[str, Any]:
        roadmap = (
            db.query(LearningRoadmap)
            .filter(LearningRoadmap.user_id == user_id)
            .order_by(LearningRoadmap.updated_at.desc())
            .first()
        )
        if roadmap:
            total = db.query(func.count(RoadmapItem.id)).filter(RoadmapItem.roadmap_id == roadmap.id).scalar() or 0
            completed = db.query(func.count(RoadmapItem.id)).filter(RoadmapItem.roadmap_id == roadmap.id, RoadmapItem.completed.is_(True)).scalar() or 0
            in_progress = db.query(func.count(RoadmapItem.id)).filter(RoadmapItem.roadmap_id == roadmap.id, RoadmapItem.started.is_(True), RoadmapItem.completed.is_(False)).scalar() or 0
            next_skill = (
                db.query(RoadmapItem)
                .filter(RoadmapItem.roadmap_id == roadmap.id, RoadmapItem.completed.is_(False))
                .order_by(RoadmapItem.sequence.asc())
                .first()
            )
            next_name = next_skill.skill.name if next_skill and next_skill.skill else "AWS Cloud Deployment"
            return {
                "roadmap": roadmap.name or "Career Roadmap",
                "completedSkills": completed,
                "totalSkills": total or completed,
                "skillsInProgress": in_progress,
                "nextRecommendedSkill": next_name,
            }
        return {"roadmap": "No roadmap yet", "completedSkills": 0, "totalSkills": 0, "skillsInProgress": 0, "nextRecommendedSkill": "Upload a resume to get started"}

    def _build_recommended_projects(self, db: Session, user_id: int) -> list[dict[str, Any]]:
        recommendation_rows = (
            db.query(Recommendation)
            .filter(Recommendation.user_id == user_id, Recommendation.type == "project")
            .order_by(Recommendation.created_at.desc())
            .limit(3)
            .all()
        )
        if recommendation_rows:
            projects = []
            for row in recommendation_rows:
                try:
                    payload = row.payload or "{}"
                    items = json.loads(payload)
                    if isinstance(items, dict):
                        projects.append({
                            "title": items.get("title") or "Project",
                            "description": items.get("description") or "Build a practical project to strengthen your portfolio.",
                            "stack": items.get("stack") or [],
                            "difficulty": items.get("difficulty") or "Intermediate",
                        })
                except Exception:
                    continue
            if projects:
                return projects
        return []

    def _build_certifications(self, db: Session, user_id: int) -> list[dict[str, Any]]:
        recommendation_rows = (
            db.query(Recommendation)
            .filter(Recommendation.user_id == user_id, Recommendation.type == "certification")
            .order_by(Recommendation.created_at.desc())
            .limit(3)
            .all()
        )
        if recommendation_rows:
            certs = []
            for row in recommendation_rows:
                try:
                    payload = row.payload or "{}"
                    items = json.loads(payload)
                    if isinstance(items, dict):
                        certs.append({
                            "title": items.get("title") or "Certification",
                            "provider": items.get("provider") or "Industry Provider",
                            "duration": items.get("duration") or "4 weeks",
                            "relevance": items.get("relevance") or "High",
                        })
                except Exception:
                    continue
            if certs:
                return certs
        return []

    def _build_recent_activity(self, db: Session, user_id: int) -> list[dict[str, str]]:
        activity = []

        recent_resume = (
            db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.uploaded_at.desc())
            .first()
        )
        if recent_resume:
            activity.append({"title": "Updated resume for target role alignment", "time": self._format_relative_time(recent_resume.uploaded_at), "type": "resume"})

        recent_readiness = (
            db.query(CareerReadiness)
            .filter(CareerReadiness.user_id == user_id)
            .order_by(CareerReadiness.updated_at.desc())
            .first()
        )
        if recent_readiness:
            activity.append({"title": "Career readiness refreshed", "time": self._format_relative_time(recent_readiness.updated_at), "type": "learning"})

        recent_match = (
            db.query(JobMatch)
            .filter(JobMatch.user_id == user_id)
            .order_by(JobMatch.updated_at.desc())
            .first()
        )
        if recent_match:
            job = db.query(Job).filter(Job.id == recent_match.job_id).first()
            if job:
                activity.append({"title": f"Matched with {job.title}", "time": self._format_relative_time(recent_match.updated_at), "type": "assessment"})

        if len(activity) >= 4:
            return activity[:4]

        return activity

    def _latest_resume_score(self, db: Session, user_id: int) -> int | None:
        latest = (
            db.query(CareerReadiness)
            .filter(CareerReadiness.user_id == user_id)
            .order_by(CareerReadiness.updated_at.desc())
            .first()
        )
        if latest and latest.resume_score is not None:
            return int(round(latest.resume_score))
        return None

    def _build_focus_from_job(self, title: str) -> str:
        title_lower = (title or "").lower()
        if "full stack" in title_lower:
            return "JavaScript, APIs, Deployment"
        if "backend" in title_lower:
            return "Node.js, Databases, Testing"
        if "frontend" in title_lower:
            return "React, Accessibility, UI Systems"
        if "cloud" in title_lower:
            return "AWS, CI/CD, Security"
        return "Role alignment and skill gap plan"

    def _format_relative_time(self, value: datetime | None) -> str:
        if value is None:
            return "Recently"
        now = datetime.now(timezone.utc)
        delta = now - value.astimezone(timezone.utc) if value.tzinfo else now - value.replace(tzinfo=timezone.utc)
        total_seconds = max(int(delta.total_seconds()), 0)
        if total_seconds < 3600:
            return f"{max(total_seconds // 60, 1)} minutes ago"
        if total_seconds < 86400:
            return f"{max(total_seconds // 3600, 1)} hours ago"
        if total_seconds < 604800:
            return f"{max(total_seconds // 86400, 1)} days ago"
        return value.strftime("%b %d")

    def _coerce_int(self, raw: Any, fallback: int) -> int:
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return int(fallback)
        return int(round(value))
