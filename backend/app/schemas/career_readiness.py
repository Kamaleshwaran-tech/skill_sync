from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ScoreBreakdown(BaseModel):
    label: str
    score: float
    maxScore: int = 100
    reason: str

    model_config = ConfigDict(from_attributes=True)


class CareerReadinessRequest(BaseModel):
    student_skills: list[str | dict[str, Any]] = []
    required_skills: list[str | dict[str, Any]] = []
    project_count: int = 0
    target_project_count: int = 3
    experience_years: float = 0.0
    target_experience_years: float = 2.0
    resume_sections: dict[str, Any] = {}
    industry_demand: dict[str, float] = {}
    target_role_match_score: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class CareerReadinessResponse(BaseModel):
    overallScore: float
    overallReason: str
    technicalScore: ScoreBreakdown
    projectScore: ScoreBreakdown
    experienceScore: ScoreBreakdown
    resumeScore: ScoreBreakdown
    industryAlignmentScore: ScoreBreakdown
    targetRoleCompatibilityScore: ScoreBreakdown
    interpretation: str
    weights: dict[str, float]

    model_config = ConfigDict(from_attributes=True)
