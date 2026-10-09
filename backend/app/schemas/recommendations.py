from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class RecommendationResource(BaseModel):
    title: str
    type: Literal["course", "article", "documentation", "project", "certification"]
    url: str | None = None
    source: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RecommendationJob(BaseModel):
    title: str
    company: str | None = None
    location: str | None = None
    remotePreference: str | None = None
    matchScore: float
    reason: str
    requiredSkills: list[str] = Field(default_factory=list)
    skillCoverage: float = 0.0
    locationFit: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RecommendationSkill(BaseModel):
    skill: str
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    reason: str
    industryDemand: float = 0.0
    prerequisites: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RecommendationProject(BaseModel):
    title: str
    goal: str
    missingSkills: list[str] = Field(default_factory=list)
    difficulty: Literal["Beginner", "Intermediate", "Advanced"]

    model_config = ConfigDict(from_attributes=True)


class RecommendationCertification(BaseModel):
    title: str
    provider: str | None = None
    focus: str | None = None
    url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(BaseModel):
    jobs: list[RecommendationJob] = Field(default_factory=list)
    skills: list[RecommendationSkill] = Field(default_factory=list)
    projects: list[RecommendationProject] = Field(default_factory=list)
    certifications: list[RecommendationCertification] = Field(default_factory=list)
    learningResources: list[RecommendationResource] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RecommendationRequest(BaseModel):
    studentSkills: list[str] = Field(default_factory=list)
    currentSkills: list[str] = Field(default_factory=list)
    missingSkills: list[str] = Field(default_factory=list)
    targetRole: str = "Software Engineer"
    preferredLocation: str | None = None
    remotePreference: str | None = None
    experienceYears: float = 0.0
    skillPriorities: dict[str, str] = Field(default_factory=dict)
    industryDemand: dict[str, float] = Field(default_factory=dict)
    jobs: list[dict[str, Any]] = Field(default_factory=list)
    profile: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)
