from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.engine import SkillSyncAIEngine
from app.models.models import (
    Job,
    Resume,
    ResumeAnalysis,
    Skill,
    UserPreference,
    UserSkill,
)
from app.services.semantic_job_matching import SemanticJobMatchingService


class DashboardService:
    """Builds the student dashboard payload: resume data + target role + AI analysis."""

    def build_dashboard(self, db: Session, user: Any) -> dict[str, Any]:
        profile = self._build_profile(db, user)
        target_role = self._get_target_role(db, user.id)
        resume_info = self._build_resume_info(db, user.id)
        skill_overview = self._build_skill_overview(db, user.id)
        recommended_jobs = self._build_recommended_jobs(db, user.id, target_role)
        last_analysis = self._load_last_analysis(db, user.id)

        return {
            "profile": profile,
            "targetRole": target_role,
            "hasResume": resume_info["has_resume"],
            "parsedSkills": resume_info["skills"],
            "personalInfo": resume_info["personal_info"],
            "skillOverview": skill_overview,
            "recommendedJobs": recommended_jobs,
            "resumeScore": resume_info["score"],
            "lastAnalysis": last_analysis,
        }

    def set_target_role(self, db: Session, user: Any, target_role: str) -> dict[str, Any]:
        clean_role = target_role.strip()
        pref = db.query(UserPreference).filter(UserPreference.user_id == user.id).one_or_none()
        if not pref:
            pref = UserPreference(user_id=user.id, preferences={})
            db.add(pref)
            db.flush()
        prefs = dict(pref.preferences or {})
        prefs["targetRole"] = clean_role
        # Keep targetRoles list for backwards compatibility with any existing code.
        prefs["targetRoles"] = [clean_role]
        pref.preferences = prefs
        db.commit()
        db.refresh(pref)
        return {"targetRole": clean_role}

    def get_target_role(self, db: Session, user: Any) -> dict[str, Any]:
        return {"targetRole": self._get_target_role(db, user.id)}

    def run_analysis(self, db: Session, user: Any) -> dict[str, Any]:
        """Compute skill gap + AI learning roadmap against the saved target role.

        Returns the full analysis payload for the dashboard. Requires an uploaded
        and parsed resume, and a saved target role.
        """
        target_role = self._get_target_role(db, user.id)
        if not target_role:
            raise ValueError("Please set a target role first.")

        resume = (
            db.query(Resume)
            .filter(Resume.user_id == user.id, Resume.status == "COMPLETED")
            .order_by(Resume.is_active.desc(), Resume.uploaded_at.desc())
            .first()
        )
        if not resume:
            raise ValueError("Please upload and analyze a resume first.")

        user_skills = [
            name for (name,) in db.query(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .filter(UserSkill.user_id == user.id)
            .all()
        ]

        # Find best-matching active jobs for the target role (title keyword match)
        jobs = db.query(Job).filter(Job.is_active.is_(True)).all()
        role_lower = target_role.lower()

        def role_match_score(job: Job) -> int:
            title = (job.title or "").lower()
            score = 0
            for token in role_lower.split():
                if len(token) >= 3 and token in title:
                    score += 1
            return score

        matched_jobs = sorted(
            jobs,
            key=lambda j: (role_match_score(j), j.created_at or datetime.min),
            reverse=True,
        )
        sample_jobs = matched_jobs[:3] if any(role_match_score(j) > 0 for j in matched_jobs) else (jobs[:3] if jobs else [])

        # Aggregate required skills from sample jobs
        required_set: dict[str, int] = {}
        for job in sample_jobs:
            for js in job.required_skills:
                if js.skill and js.skill_type == "required":
                    name = (js.skill.name or "").strip()
                    if name:
                        required_set[name.lower()] = js.skill.name
        required = list(required_set.values())

        # Fall back to a generic skill list for the role if no jobs match
        if not required:
            required = self._default_role_skills(target_role)

        user_set = {s.lower() for s in user_skills}
        missing = [s for s in required if s.lower() not in user_set]

        # Classify priority: first third high, next third medium, rest low
        prioritized: list[dict[str, str]] = []
        for idx, skill in enumerate(missing[:12]):
            if idx < max(1, len(missing) // 3):
                prio = "HIGH"
            elif idx < max(2, (2 * len(missing)) // 3):
                prio = "MEDIUM"
            else:
                prio = "LOW"
            prioritized.append({"skill": skill, "priority": prio})

        # Build roadmap via the AI engine (Gemini when key present, rule-based fallback otherwise)
        roadmap_payload = None
        try:
            engine = SkillSyncAIEngine()
            skill_priorities = {item["skill"]: item["priority"] for item in prioritized}
            roadmap_result = engine.generate_learning_roadmap(
                target_role=target_role,
                student_skills=user_skills,
                missing_skills_with_priority=[{"name": s["skill"], "priority": s["priority"]} for s in prioritized],
                career_readiness_score=0.0,
            )
            if roadmap_result:
                roadmap_result = engine.llm_provider.enhance_roadmap_advice(roadmap_result) if hasattr(engine, "llm_provider") else roadmap_result
                roadmap_payload = roadmap_result
        except Exception as exc:  # pragma: no cover - best effort
            roadmap_payload = {
                "target_role": target_role,
                "summary": f"Focus on closing {len(missing)} key skill gaps to prepare for {target_role} roles.",
                "roadmap_steps": [
                    {
                        "skill": item["skill"],
                        "priority": item["priority"],
                        "description": f"Build core proficiency in {item['skill']} for {target_role}.",
                    }
                    for item in prioritized[:8]
                ],
                "career_advice": f"Start with the HIGH priority skills first, then build portfolio projects targeting {target_role}.",
            }

        analysis = {
            "targetRole": target_role,
            "skillGap": prioritized,
            "matchedSkills": [s for s in user_skills if s.lower() in {r.lower() for r in required}] or user_skills[:10],
            "roadmap": roadmap_payload,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
        }
        return analysis

    # ----- internal helpers -----

    def _get_target_role(self, db: Session, user_id: int) -> str | None:
        pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).one_or_none()
        if not pref:
            return None
        prefs = pref.preferences or {}
        role = prefs.get("targetRole")
        if role and str(role).strip():
            return str(role).strip()
        roles = prefs.get("targetRoles") or []
        return str(roles[0]).strip() if roles else None

    def _build_profile(self, db: Session, user: Any) -> dict[str, str]:
        name = user.full_name or user.email.split("@")[0].title()
        role = "Student" if not getattr(user, "role", None) else str(user.role).replace("_", " ").title()
        return {
            "name": name,
            "role": role,
            "lastUpdated": "Updated today",
            "focus": "Add a target role to generate your skill gap and roadmap",
        }

    def _build_resume_info(self, db: Session, user_id: int) -> dict[str, Any]:
        resume = (
            db.query(Resume)
            .filter(Resume.user_id == user_id, Resume.status == "COMPLETED")
            .order_by(Resume.is_active.desc(), Resume.uploaded_at.desc())
            .first()
        )
        if not resume:
            return {"has_resume": False, "skills": [], "personal_info": {}, "score": None}

        user_skills = [
            name for (name,) in db.query(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .filter(UserSkill.user_id == user_id, UserSkill.source == "resume")
            .order_by(Skill.name.asc())
            .all()
        ]

        personal_info: dict[str, Any] = {}
        latest_analysis = (
            db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.resume_id == resume.id)
            .order_by(ResumeAnalysis.created_at.desc())
            .first()
        )
        score = None
        if latest_analysis and latest_analysis.profile:
            profile = latest_analysis.profile or {}
            pi = profile.get("personal_info") or {}
            personal_info = {
                "name": profile.get("name"),
                "email": None,
                "phone": pi.get("phone"),
                "location": pi.get("location"),
                "linkedin": pi.get("linkedin"),
                "summary": profile.get("summary"),
                "experienceCount": len(profile.get("experience") or []),
                "projectCount": len(profile.get("projects") or []),
                "educationCount": len(profile.get("education") or []),
            }
            if latest_analysis.confidence is not None:
                score = int(round(float(latest_analysis.confidence) * 100))
        return {
            "has_resume": True,
            "skills": user_skills,
            "personal_info": personal_info,
            "score": score,
        }

    def _build_skill_overview(self, db: Session, user_id: int) -> dict[str, list[str]]:
        current = [
            name for (name,) in db.query(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .filter(UserSkill.user_id == user_id)
            .order_by(Skill.name.asc())
            .limit(12)
            .all()
        ]
        return {"current": current, "strong": [], "developing": [], "missing": []}

    def _build_recommended_jobs(self, db: Session, user_id: int, target_role: str | None) -> list[dict[str, Any]]:
        resume = (
            db.query(Resume)
            .filter(Resume.user_id == user_id, Resume.status == "COMPLETED")
            .order_by(Resume.is_active.desc(), Resume.uploaded_at.desc())
            .first()
        )
        jobs_query = db.query(Job).filter(Job.is_active.is_(True))
        if target_role:
            # Prefer jobs whose title contains target role tokens
            tokens = [t for t in target_role.lower().split() if len(t) >= 3]
            if tokens:
                from sqlalchemy import or_
                filters = [Job.title.ilike(f"%{t}%") for t in tokens]
                jobs_query = jobs_query.filter(or_(*filters))
        jobs = jobs_query.order_by(Job.created_at.desc()).limit(20).all()
        if not jobs:
            jobs = db.query(Job).filter(Job.is_active.is_(True)).order_by(Job.created_at.desc()).limit(10).all()

        if not resume:
            return [
                {
                    "title": j.title or "Role",
                    "company": j.company or "Company",
                    "location": j.location or "Remote",
                    "match": 0,
                    "requiredSkills": [],
                }
                for j in jobs[:3]
            ]

        user_skills = [
            name for (name,) in db.query(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .filter(UserSkill.user_id == user_id).all()
        ]
        matcher = SemanticJobMatchingService()
        results = []
        for job in jobs:
            required = [js.skill.name for js in job.required_skills if js.skill and js.skill_type == "required"]
            preferred = [js.skill.name for js in job.required_skills if js.skill and js.skill_type == "preferred"]
            r = matcher.calculate(
                {"skills": user_skills, "resume_text": resume.parsed_text or ""},
                {"description": job.description or "", "required_skills": required, "preferred_skills": preferred},
            )
            results.append((job, r))
        results.sort(key=lambda x: x[1]["overall_match_score"], reverse=True)
        return [
            {
                "title": job.title,
                "company": job.company or "Unknown Company",
                "location": job.location or "Remote",
                "match": int(round(r["overall_match_score"])),
                "requiredSkills": r.get("matched_skills", []) + r.get("missing_skills", []),
            }
            for job, r in results[:3]
        ]

    def _load_last_analysis(self, db: Session, user_id: int) -> dict[str, Any] | None:
        # We don't persist full analyses yet; return None so frontend shows "run analysis" CTA.
        return None

    def _default_role_skills(self, role: str) -> list[str]:
        """Sensible fallback skills when no matching jobs are in the DB yet."""
        r = role.lower()
        if "data" in r and ("scientist" in r or "science" in r):
            return ["Python", "SQL", "Pandas", "NumPy", "Scikit-learn", "Machine Learning", "Statistics", "Data Visualization"]
        if "data analyst" in r or "analyst" in r:
            return ["SQL", "Python", "Excel", "Tableau", "Power BI", "Data Visualization", "Statistics"]
        if "frontend" in r:
            return ["HTML", "CSS", "JavaScript", "React", "TypeScript", "Responsive Design", "Git"]
        if "backend" in r:
            return ["Python", "SQL", "REST APIs", "Databases", "Git", "Docker", "Testing"]
        if "full stack" in r or "fullstack" in r:
            return ["JavaScript", "React", "Node.js", "SQL", "REST APIs", "Git", "HTML", "CSS"]
        if "devops" in r or "cloud" in r or "sre" in r:
            return ["Linux", "Docker", "Kubernetes", "AWS", "CI/CD", "Terraform", "Networking"]
        if "ml" in r or "machine learning" in r or "ai" in r:
            return ["Python", "Machine Learning", "PyTorch", "TensorFlow", "Scikit-learn", "NumPy", "MLOps"]
        if "mobile" in r or "android" in r or "ios" in r:
            return ["Kotlin", "Swift", "React Native", "REST APIs", "Git", "Mobile UI"]
        # Generic software-engineer default
        return ["Python", "SQL", "Git", "Data Structures", "Algorithms", "REST APIs", "JavaScript"]
