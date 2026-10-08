from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict


class BaseConfig:
    model_config = ConfigDict(from_attributes=True)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None
    role: Literal["CANDIDATE"] = "CANDIDATE"

    model_config = BaseConfig.model_config


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = BaseConfig.model_config


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = BaseConfig.model_config


class RefreshRequest(BaseModel):
    refresh_token: str

    model_config = BaseConfig.model_config


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    avatar_url: Optional[str]
    role: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = BaseConfig.model_config
