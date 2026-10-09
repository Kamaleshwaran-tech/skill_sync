from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel


class CareerReadinessBreakdown(BaseModel):
    overall_score: float
    skill_match_score: float
    project_relevance_score: float
    resume_quality_score: float
    industry_demand_score: float
    details: Dict[str, Any]


class CareerReadinessEngineInterface(ABC):
    """Abstract interface for calculating Career Readiness Score."""

    @abstractmethod
    def calculate_readiness(self, student_profile: Dict[str, Any], target_roles_data: Dict[str, Any]) -> CareerReadinessBreakdown:
        """Calculate Career Readiness Score based on skill match, project relevance, resume quality, and industry demand."""
        pass
