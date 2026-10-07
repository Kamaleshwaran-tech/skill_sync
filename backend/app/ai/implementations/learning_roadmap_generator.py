from __future__ import annotations

from typing import Any, Dict, List
from app.ai.interfaces.roadmap_generator import LearningRoadmap, RoadmapGeneratorInterface, RoadmapStep


class LearningRoadmapGenerator(RoadmapGeneratorInterface):
    """Generates personalized step-by-step learning roadmaps based on prioritized skill gaps."""

    def generate_roadmap(
        self,
        target_role: str,
        student_skills: List[str],
        missing_skills_with_priority: List[Dict[str, Any]],
        career_readiness_score: float = 0.0,
    ) -> LearningRoadmap:
        steps: List[RoadmapStep] = []

        for idx, gap in enumerate(missing_skills_with_priority[:5], start=1):
            skill_name = gap.get("skill") or gap.get("name") or f"Skill {idx}"
            priority = gap.get("priority", "MEDIUM")
            duration = "2-3 weeks" if priority == "HIGH" else "1-2 weeks"
            difficulty = "Intermediate" if priority == "HIGH" else "Beginner"

            steps.append(
                RoadmapStep(
                    order=idx,
                    skill=skill_name,
                    description=f"Master {skill_name} fundamentals and integrate into a role-relevant portfolio project for {target_role}.",
                    priority=priority,
                    difficulty=difficulty,
                    estimated_duration=duration,
                    prerequisites=[],
                    project_recommendation=f"Build a practical {skill_name} application for {target_role}.",
                    completion_status="not_started",
                )
            )

        if not steps:
            steps.append(
                RoadmapStep(
                    order=1,
                    skill="Advanced System Architecture",
                    description=f"Refactor existing projects and deepen system design capabilities for {target_role}.",
                    priority="MEDIUM",
                    difficulty="Advanced",
                    estimated_duration="3-4 weeks",
                    project_recommendation=f"End-to-end full-stack benchmark project for {target_role}.",
                )
            )

        summary = f"Customized {len(steps)}-step learning roadmap to achieve readiness for {target_role}."
        advice = f"Focus on completing HIGH priority skills first to maximize your readiness score from {career_readiness_score:.0f}%."

        return LearningRoadmap(
            target_role=target_role,
            current_skill_level="Intermediate" if career_readiness_score >= 60 else "Emerging",
            summary=summary,
            steps=steps,
            career_advice=advice,
            readiness_score=career_readiness_score,
        )
