from __future__ import annotations

from typing import Any

from app.config.settings import get_settings


class CareerReadinessService:
    def __init__(self, weights: dict[str, float] | None = None):
        settings = get_settings()
        defaults = {
            "technical": settings.career_technical_weight,
            "project": settings.career_project_weight,
            "experience": settings.career_experience_weight,
            "resume": settings.career_resume_weight,
            "industry": settings.career_industry_weight,
            "role": settings.career_role_weight,
        }
        self.weights = {**defaults, **(weights or {})}

    def calculate(self, profile: dict[str, Any]) -> dict[str, Any]:
        technical = self._technical_score(profile)
        project = self._project_score(profile)
        experience = self._experience_score(profile)
        resume = self._resume_score(profile)
        industry = self._industry_alignment_score(profile)
        role = self._target_role_score(profile)

        overall = (
            technical["score"] * self.weights["technical"]
            + project["score"] * self.weights["project"]
            + experience["score"] * self.weights["experience"]
            + resume["score"] * self.weights["resume"]
            + industry["score"] * self.weights["industry"]
            + role["score"] * self.weights["role"]
        )

        overall_score = self._clamp(round(overall, 2), 0.0, 100.0)

        return {
            "overallScore": overall_score,
            "overallReason": self._overall_reason(overall_score),
            "technicalScore": technical,
            "projectScore": project,
            "experienceScore": experience,
            "resumeScore": resume,
            "industryAlignmentScore": industry,
            "targetRoleCompatibilityScore": role,
            "interpretation": "This score is a compatibility and readiness indicator, not a scientific prediction of hiring probability.",
            "weights": self.weights,
        }

    def _technical_score(self, profile: dict[str, Any]) -> dict[str, Any]:
        required_skills = self._normalize_names(profile.get("required_skills", []))
        student_skills = self._normalize_names(profile.get("student_skills", []))
        if not required_skills:
            score = 100.0 if not student_skills else 80.0
            reason = "No explicit target-skill list was provided, so the score reflects the current profile strength and skill coverage quality."
        else:
            matched = set(student_skills) & set(required_skills)
            score = round((len(matched) / len(required_skills)) * 100.0, 2)
            reason = (
                f"The student possesses {score:.0f}% of the high-priority skills found in the analyzed target roles."
            )
        return self._score_block("Technical Skills", score, reason)

    def _project_score(self, profile: dict[str, Any]) -> dict[str, Any]:
        project_count = int(profile.get("project_count", 0) or 0)
        target_projects = max(1, int(profile.get("target_project_count", 3) or 3))
        score = self._clamp((project_count / target_projects) * 100.0, 0.0, 100.0)
        reason = (
            f"The student has {project_count} project(s) mapped to the target role; a stronger portfolio would improve the readiness score."
        )
        return self._score_block("Project Relevance", score, reason)

    def _experience_score(self, profile: dict[str, Any]) -> dict[str, Any]:
        experience_years = float(profile.get("experience_years", 0) or 0)
        target_years = float(profile.get("target_experience_years", 2) or 2)
        score = self._clamp((experience_years / max(target_years, 1.0)) * 100.0, 0.0, 100.0)
        reason = (
            f"The student has {experience_years:.1f} years of relevant experience against a target benchmark of {target_years:.1f} years."
        )
        return self._score_block("Experience Relevance", score, reason)

    def _resume_score(self, profile: dict[str, Any]) -> dict[str, Any]:
        sections = profile.get("resume_sections", {})
        required_sections = [
            "summary",
            "skills",
            "experience",
            "education",
            "projects",
            "certifications",
        ]
        present = sum(1 for section in required_sections if bool(sections.get(section)))
        score = round((present / len(required_sections)) * 100.0, 2)
        reason = (
            f"The resume includes {present}/{len(required_sections)} key sections needed for strong role alignment and recruiter readability."
        )
        return self._score_block("Resume Completeness", score, reason)

    def _industry_alignment_score(self, profile: dict[str, Any]) -> dict[str, Any]:
        skill_demand = profile.get("industry_demand", {}) or {}
        student_skills = self._normalize_names(profile.get("student_skills", []))
        if not student_skills:
            score = 0.0
            reason = "No skill-demand data is available for the current profile, so the industry alignment score is not yet measurable."
        else:
            relevant_values = [float(skill_demand.get(skill, 0.0)) for skill in student_skills if skill in skill_demand]
            score = round((sum(relevant_values) / max(len(relevant_values), 1)) * 100.0, 2) if relevant_values else 0.0
            reason = (
                f"The student’s current skill profile aligns with an average industry demand of {score:.0f}% across mapped skills."
            )
        return self._score_block("Industry Alignment", score, reason)

    def _target_role_score(self, profile: dict[str, Any]) -> dict[str, Any]:
        target_match = float(profile.get("target_role_match_score", 0.0) or 0.0)
        score = self._clamp(target_match, 0.0, 100.0)
        reason = (
            f"The current target-role compatibility score is {score:.0f}/100, based on role-specific match signals and gap analysis."
        )
        return self._score_block("Target Role Compatibility", score, reason)

    def _overall_reason(self, score: float) -> str:
        if score >= 85:
            return "The student is highly positioned for role readiness and needs only focused optimization in a few priority gaps."
        if score >= 70:
            return "The student is reasonably ready for the target role, with a manageable set of skill investments still needed."
        if score >= 50:
            return "The student shows solid potential, but significant role-specific skill development is still recommended."
        return "The student is early in the readiness journey and should prioritize foundational skill-building before target-role applications."

    def _score_block(self, label: str, score: float, reason: str) -> dict[str, Any]:
        normalized = self._clamp(float(score), 0.0, 100.0)
        return {
            "label": label,
            "score": round(normalized, 2),
            "maxScore": 100,
            "reason": reason,
        }

    def _normalize_names(self, items: list[str | dict[str, Any]]) -> list[str]:
        normalized: list[str] = []
        for item in items or []:
            if isinstance(item, str):
                normalized.append(item.strip().lower())
            elif isinstance(item, dict):
                name = item.get("name") or item.get("skill")
                if name:
                    normalized.append(str(name).strip().lower())
        return normalized

    def _clamp(self, value: float, lower: float, upper: float) -> float:
        return max(lower, min(upper, float(value)))
