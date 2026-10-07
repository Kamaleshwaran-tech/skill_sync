from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel


class PrioritySkillGap(BaseModel):
    skill: str
    priority: str  # HIGH, MEDIUM, LOW
    kind: str      # required vs preferred
    reason: str
    recommended_order: int
    current_proficiency: float = 0.0
    required_proficiency: float = 3.0
    gap_percentage: float = 0.0
    industry_demand: float = 0.5


class SkillGapAnalyzerInterface(ABC):
    """Abstract interface for identifying missing skills with priority levels."""

    @abstractmethod
    def analyze_gaps(
        self,
        student_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str],
        industry_demand: Dict[str, float],
    ) -> List[PrioritySkillGap]:
        """Analyze skill gaps and assign priority levels (HIGH, MEDIUM, LOW)."""
        pass
