from __future__ import annotations

from typing import Any, Dict
from app.ai.interfaces.scoring_engine import CareerReadinessBreakdown, CareerReadinessEngineInterface


class CareerReadinessEngine(CareerReadinessEngineInterface):
    """Calculates Career Readiness Score based on skill match, project relevance, resume quality, and industry demand."""

    def __init__(self, weights: Dict[str, float] | None = None):
        self.weights = weights or {
            "skill_match": 0.40,
            "project_relevance": 0.20,
            "resume_quality": 0.20,
            "industry_demand": 0.20,
        }

    def calculate_readiness(
        self,
        student_profile: Dict[str, Any],
        target_roles_data: Dict[str, Any],
    ) -> CareerReadinessBreakdown:
        student_skills = {s.strip().lower() for s in student_profile.get("skills", []) if isinstance(s, str)}
        for s in student_profile.get("technical_skills", []):
            if isinstance(s, dict) and s.get("name"):
                student_skills.add(s["name"].strip().lower())
            elif isinstance(s, str):
                student_skills.add(s.strip().lower())

        required_skills = {s.strip().lower() for s in target_roles_data.get("required_skills", [])}

        # 1. Skill Match Score (0 - 100)
        if required_skills:
            matched = student_skills & required_skills
            skill_score = (len(matched) / len(required_skills)) * 100.0
        else:
            skill_score = 80.0 if student_skills else 50.0

        # 2. Project Relevance Score (0 - 100)
        projects = student_profile.get("projects", [])
        project_count = len(projects) if isinstance(projects, list) else int(student_profile.get("project_count", 0))
        project_score = min(100.0, (project_count / 3.0) * 100.0)

        # 3. Resume Quality Score (0 - 100)
        sections = student_profile.get("sections", {}) or student_profile.get("resume_sections", {})
        required_secs = ["education", "experience", "skills", "projects"]
        present_secs = sum(1 for s in required_secs if bool(sections.get(s)))
        resume_score = (present_secs / len(required_secs)) * 100.0 if required_secs else 80.0
        if not sections and student_profile.get("raw_text"):
            resume_score = 85.0

        # 4. Industry Demand Score (0 - 100)
        demand_map = target_roles_data.get("industry_demand", {})
        if demand_map and student_skills:
            demand_vals = [float(demand_map.get(s, 0.5)) for s in student_skills if s in demand_map]
            industry_score = (sum(demand_vals) / max(1, len(demand_vals))) * 100.0 if demand_vals else 70.0
        else:
            industry_score = 75.0

        overall = (
            skill_score * self.weights["skill_match"]
            + project_score * self.weights["project_relevance"]
            + resume_score * self.weights["resume_quality"]
            + industry_score * self.weights["industry_demand"]
        )

        overall = round(max(0.0, min(100.0, overall)), 2)

        return CareerReadinessBreakdown(
            overall_score=overall,
            skill_match_score=round(skill_score, 2),
            project_relevance_score=round(project_score, 2),
            resume_quality_score=round(resume_score, 2),
            industry_demand_score=round(industry_score, 2),
            details={
                "target_role": target_roles_data.get("role_title", "Software Engineer"),
                "weights": self.weights,
                "matched_skills_count": len(student_skills & required_skills) if required_skills else len(student_skills),
                "total_required_skills": len(required_skills),
            }
        )
