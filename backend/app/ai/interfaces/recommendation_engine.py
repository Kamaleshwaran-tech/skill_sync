from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendedResource(BaseModel):
    title: str
    type: str  # course, documentation, project, tutorial
    url: Optional[str] = None
    source: str = ""


class RecommendedProject(BaseModel):
    title: str
    goal: str
    missing_skills: List[str] = Field(default_factory=list)
    difficulty: str = "Intermediate"


class RecommendedCertification(BaseModel):
    title: str
    skill: str
    issuer: str = ""
    url: Optional[str] = None


class RecommendationPayload(BaseModel):
    projects: List[RecommendedProject] = Field(default_factory=list)
    certifications: List[RecommendedCertification] = Field(default_factory=list)
    resources: List[RecommendedResource] = Field(default_factory=list)


class RecommendationEngineInterface(ABC):
    """Abstract interface for recommending projects, certifications, and learning resources."""

    @abstractmethod
    def generate_recommendations(
        self,
        target_role: str,
        missing_skills: List[str],
        current_skills: List[str],
    ) -> RecommendationPayload:
        """Generate targeted recommendations based on skill gaps and career goal."""
        pass
