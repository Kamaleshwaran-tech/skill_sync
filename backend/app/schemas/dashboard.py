from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DashboardProfile(BaseModel):
    name: str
    role: str
    lastUpdated: str
    focus: str

    model_config = ConfigDict(from_attributes=True)


class DashboardMetric(BaseModel):
    label: str
    value: int
    trend: str

    model_config = ConfigDict(from_attributes=True)


class DashboardReadiness(BaseModel):
    overall: int
    metrics: list[DashboardMetric] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DashboardCareerMatch(BaseModel):
    role: str
    match: int
    skillGapCount: int
    focus: str

    model_config = ConfigDict(from_attributes=True)


class DashboardSkillOverview(BaseModel):
    current: list[str] = Field(default_factory=list)
    strong: list[str] = Field(default_factory=list)
    developing: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DashboardRecommendedJob(BaseModel):
    title: str
    company: str
    location: str
    match: int
    requiredSkills: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DashboardSkillDemandItem(BaseModel):
    skill: str
    demand: int

    model_config = ConfigDict(from_attributes=True)


class DashboardLearningProgress(BaseModel):
    roadmap: str
    completedSkills: int
    totalSkills: int
    skillsInProgress: int
    nextRecommendedSkill: str

    model_config = ConfigDict(from_attributes=True)


class DashboardProject(BaseModel):
    title: str
    description: str
    stack: list[str] = Field(default_factory=list)
    difficulty: str

    model_config = ConfigDict(from_attributes=True)


class DashboardCertification(BaseModel):
    title: str
    provider: str
    duration: str
    relevance: str

    model_config = ConfigDict(from_attributes=True)


class DashboardActivity(BaseModel):
    title: str
    time: str
    type: str

    model_config = ConfigDict(from_attributes=True)


class TargetRoleRequest(BaseModel):
    targetRole: str = Field(min_length=2, max_length=100)

    model_config = ConfigDict(from_attributes=True)


class TargetRoleResponse(BaseModel):
    targetRole: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SkillGapItem(BaseModel):
    skill: str
    priority: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"

    model_config = ConfigDict(from_attributes=True)


class DashboardAnalysisResponse(BaseModel):
    targetRole: str
    skillGap: list[SkillGapItem] = Field(default_factory=list)
    matchedSkills: list[str] = Field(default_factory=list)
    roadmap: dict[str, Any] | None = None
    generatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    profile: DashboardProfile
    targetRole: str | None = None
    hasResume: bool = False
    parsedSkills: list[str] = Field(default_factory=list)
    personalInfo: dict[str, Any] = Field(default_factory=dict)
    skillOverview: DashboardSkillOverview
    recommendedJobs: list[DashboardRecommendedJob] = Field(default_factory=list)
    resumeScore: int | None = None
    lastAnalysis: DashboardAnalysisResponse | None = None

    model_config = ConfigDict(from_attributes=True)
