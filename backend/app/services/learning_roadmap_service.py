from __future__ import annotations

from typing import Any


class LearningRoadmapPlanningService:
    """Build deterministic roadmap context before any LLM reasoning."""

    def build_context(self, payload: dict[str, Any]) -> dict[str, Any]:
        current_skills = [str(skill).strip() for skill in payload.get("currentSkills", []) if str(skill).strip()]
        target_role = str(payload.get("targetRole") or "Software Engineer")
        missing_skills = [str(skill).strip() for skill in payload.get("missingSkills", []) if str(skill).strip()]
        if not missing_skills:
            missing_skills = [str(skill).strip() for skill in payload.get("requiredSkills", []) if str(skill).strip() and str(skill).strip().lower() not in {s.lower() for s in current_skills}]

        priorities = payload.get("skillPriorities", {}) or {}
        dependencies = payload.get("skillDependencies", {}) or {}
        demand = payload.get("industryDemand", {}) or {}
        readiness_score = float(payload.get("careerReadinessScore", 0.0) or 0.0)

        normalized_priorities = {str(key).strip(): str(value).upper() for key, value in priorities.items() if str(key).strip()}
        ordered_missing = sorted(
            missing_skills,
            key=lambda skill: self._priority_rank(normalized_priorities.get(skill, "MEDIUM")),
            reverse=True,
        )

        skill_entries = []
        for skill in ordered_missing:
            skill_entries.append(
                {
                    "skill": skill,
                    "priority": normalized_priorities.get(skill, "MEDIUM"),
                    "industryDemand": float(demand.get(skill, 0.5) or 0.5),
                    "dependencies": [str(dep).strip() for dep in dependencies.get(skill, []) if str(dep).strip()],
                    "recommendedOrder": ordered_missing.index(skill) + 1,
                }
            )

        return {
            "currentSkills": current_skills,
            "targetRole": target_role,
            "missingSkills": ordered_missing,
            "skillPriorities": normalized_priorities,
            "skillDependencies": {str(key).strip(): [str(dep).strip() for dep in value if str(dep).strip()] for key, value in dependencies.items()},
            "industryDemand": {str(key).strip(): float(value) for key, value in demand.items() if str(key).strip()},
            "careerReadinessScore": readiness_score,
            "recommendedLearningOrder": [item["skill"] for item in skill_entries],
            "deterministicSummary": self._summary(target_role, current_skills, ordered_missing, readiness_score),
        }

    def _priority_rank(self, priority: str) -> int:
        return {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(str(priority).upper(), 2)

    def _summary(self, target_role: str, current_skills: list[str], missing_skills: list[str], readiness_score: float) -> str:
        if not missing_skills:
            return f"The student already covers the essential requirements for {target_role} and should focus on mastery and portfolio depth."
        return (
            f"The student is preparing for {target_role} with {len(current_skills)} current skills. "
            f"Priority focus should go to {', '.join(missing_skills[:3])} to raise readiness from {readiness_score:.0f}/100."
        )
