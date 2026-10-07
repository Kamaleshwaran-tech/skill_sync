from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class RoadmapResource(BaseModel):
    title: str
    type: Literal["course", "article", "project", "documentation", "certification"]
    url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RoadmapStep(BaseModel):
    order: int
    skill: str
    description: str
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    difficulty: Literal["Beginner", "Intermediate", "Advanced"]
    estimatedDuration: str
    prerequisites: list[str] = Field(default_factory=list)
    learningResources: list[RoadmapResource] = Field(default_factory=list)
    projectRecommendation: str
    completionStatus: Literal["not_started", "in_progress", "completed"] = "not_started"

    model_config = ConfigDict(from_attributes=True)


class LearningRoadmapResponse(BaseModel):
    targetRole: str
    currentSkillLevel: str
    summary: str
    learningSequence: list[RoadmapStep]
    projectRecommendations: list[str]
    certificationRecommendations: list[str]
    careerAdvice: str
    readinessScore: float
    generatedAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class RoadmapGenerationRequest(BaseModel):
    currentSkills: list[str] = Field(default_factory=list)
    targetRole: str = "Software Engineer"
    missingSkills: list[str] = Field(default_factory=list)
    skillPriorities: dict[str, str] = Field(default_factory=dict)
    skillDependencies: dict[str, list[str]] = Field(default_factory=dict)
    industryDemand: dict[str, float] = Field(default_factory=dict)
    careerReadinessScore: float = 0.0
    requiredSkills: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
