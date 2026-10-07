from __future__ import annotations

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


class DashboardResponse(BaseModel):
    profile: DashboardProfile
    readiness: DashboardReadiness
    careerMatches: list[DashboardCareerMatch] = Field(default_factory=list)
    skillOverview: DashboardSkillOverview
    recommendedJobs: list[DashboardRecommendedJob] = Field(default_factory=list)
    skillDemand: list[DashboardSkillDemandItem] = Field(default_factory=list)
    learningProgress: DashboardLearningProgress
    recommendedProjects: list[DashboardProject] = Field(default_factory=list)
    certifications: list[DashboardCertification] = Field(default_factory=list)
    recentActivity: list[DashboardActivity] = Field(default_factory=list)
    resumeScore: int | None = None
    careerReadinessScore: int | None = None

    model_config = ConfigDict(from_attributes=True)
