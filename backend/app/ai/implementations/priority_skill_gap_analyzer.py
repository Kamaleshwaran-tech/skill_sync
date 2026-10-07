from __future__ import annotations

from typing import Any, Dict, List
from app.ai.interfaces.skill_gap_analyzer import PrioritySkillGap, SkillGapAnalyzerInterface


class PrioritySkillGapAnalyzer(SkillGapAnalyzerInterface):
    """Identifies missing skills and assigns priority levels (HIGH, MEDIUM, LOW)."""

    def analyze_gaps(
        self,
        student_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str],
        industry_demand: Dict[str, float],
    ) -> List[PrioritySkillGap]:
        current_set = {s.strip().lower() for s in student_skills}
        req_set = {s.strip().lower() for s in required_skills}
        pref_set = {s.strip().lower() for s in preferred_skills}

        missing_req = sorted(list(req_set - current_set))
        missing_pref = sorted(list(pref_set - current_set - req_set))

        gaps: List[PrioritySkillGap] = []

        for idx, skill in enumerate(missing_req):
            demand = float(industry_demand.get(skill, 0.7))
            priority = "HIGH" if demand >= 0.6 else "MEDIUM"
            gaps.append(
                PrioritySkillGap(
                    skill=skill.title() if len(skill) > 3 else skill.upper(),
                    priority=priority,
                    kind="required",
                    reason=f"Mandatory required skill for role with market demand of {demand:.0%}.",
                    recommended_order=idx + 1,
                    current_proficiency=0.0,
                    required_proficiency=3.0,
                    gap_percentage=100.0,
                    industry_demand=demand,
                )
            )

        start_order = len(gaps) + 1
        for idx, skill in enumerate(missing_pref):
            demand = float(industry_demand.get(skill, 0.4))
            priority = "MEDIUM" if demand >= 0.6 else "LOW"
            gaps.append(
                PrioritySkillGap(
                    skill=skill.title() if len(skill) > 3 else skill.upper(),
                    priority=priority,
                    kind="preferred",
                    reason=f"Preferred nice-to-have skill with market demand of {demand:.0%}.",
                    recommended_order=start_order + idx,
                    current_proficiency=0.0,
                    required_proficiency=2.0,
                    gap_percentage=100.0,
                    industry_demand=demand,
                )
            )

        # Sort by HIGH -> MEDIUM -> LOW, then demand
        priority_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        gaps.sort(key=lambda g: (priority_rank.get(g.priority, 0), g.industry_demand), reverse=True)

        for i, g in enumerate(gaps, start=1):
            g.recommended_order = i

        return gaps
