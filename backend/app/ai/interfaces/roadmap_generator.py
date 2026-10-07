from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class RoadmapStep(BaseModel):
    order: int
    skill: str
    description: str
    priority: str
    difficulty: str
    estimated_duration: str
    prerequisites: List[str] = Field(default_factory=list)
    project_recommendation: str = ""
    completion_status: str = "not_started"


class LearningRoadmap(BaseModel):
    target_role: str
    current_skill_level: str
    summary: str
    steps: List[RoadmapStep] = Field(default_factory=list)
    career_advice: str = ""
    readiness_score: float = 0.0


class RoadmapGeneratorInterface(ABC):
    """Abstract interface for generating personalized learning roadmaps."""

    @abstractmethod
    def generate_roadmap(
        self,
        target_role: str,
        student_skills: List[str],
        missing_skills_with_priority: List[Dict[str, Any]],
        career_readiness_score: float = 0.0,
    ) -> LearningRoadmap:
        """Generate a structured personalized learning roadmap."""
        pass
