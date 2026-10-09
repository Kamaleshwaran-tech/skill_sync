from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class SkillProficiency(BaseModel):
    name: str
    proficiency: float = 3.0

    model_config = ConfigDict(from_attributes=True)


class SkillGapJobInput(BaseModel):
    title: str
    required_skills: list[str | SkillProficiency] = []
    preferred_skills: list[str | SkillProficiency] = []

    model_config = ConfigDict(from_attributes=True)


class SkillGapAnalysisRequest(BaseModel):
    student_skills: list[str | SkillProficiency] = []
    jobs: list[SkillGapJobInput] = []
    job_market_demand: dict[str, float] = {}
    prerequisites: dict[str, list[str]] = {}

    model_config = ConfigDict(from_attributes=True)


class SkillGapDetail(BaseModel):
    skill: str
    kind: Literal["required", "preferred"]
    priority: str
    reason: str
    industryDemand: float
    recommendedOrder: int
    currentProficiency: float
    requiredProficiency: float
    gap: float


class JobSkillGapAnalysis(BaseModel):
    jobTitle: str
    currentSkills: list[str]
    requiredSkills: list[str]
    matchedSkills: list[str]
    missingSkills: list[str]
    preferredMissingSkills: list[str]
    gaps: list[SkillGapDetail]


class SkillGapAnalysisResponse(BaseModel):
    jobs: list[JobSkillGapAnalysis]
