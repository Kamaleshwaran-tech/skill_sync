from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class BaseConfig:
    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = BaseConfig.model_config


class SkillSchema(BaseModel):
    id: int
    name: str
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = BaseConfig.model_config


class ResumeSchema(BaseModel):
    id: int
    user_id: int
    filename: str
    file_type: str
    file_size: Optional[int]
    uploaded_at: datetime
    processed: bool

    model_config = BaseConfig.model_config


class JobSchema(BaseModel):
    id: int
    source_id: Optional[int]
    external_id: Optional[str]
    title: str
    company: Optional[str]
    location: Optional[str]
    job_type: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    posted_date: Optional[date]

    model_config = BaseConfig.model_config


class JobMatchSchema(BaseModel):
    id: int
    user_id: int
    job_id: int
    match_score: Optional[float]
    matched_skills_count: Optional[int]
    missing_skills_count: Optional[int]
    created_at: datetime

    model_config = BaseConfig.model_config
