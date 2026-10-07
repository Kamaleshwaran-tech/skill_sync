from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="SkillSync AI")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    api_prefix: str = Field(default="/api/v1")
    docs_url: str | None = Field(default="/api/v1/docs")
    redoc_url: str | None = Field(default="/api/v1/redoc")
    openapi_url: str | None = Field(default="/api/v1/openapi.json")
    database_url: str = Field(default="sqlite:///./skillsync_ai.db")
    db_echo: bool = Field(default=False)
    cors_origins: str | list[str] = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://[::1]:5173,http://localhost:3000,http://127.0.0.1:3000,http://[::1]:3000"
    )
    allow_credentials: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    rate_limit_per_minute: int = Field(default=60)
    rate_limit_burst: int = Field(default=120)
    auto_seed_data: bool = Field(default=False)

    # JWT settings
    jwt_secret_key: str = Field(default="")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_days: int = Field(default=30)

    # Resume storage
    resume_storage_dir: str = Field(default="./storage/resumes")
    resume_max_upload_mb: int = Field(default=5)



    # Job ingestion provider settings
    job_providers: str | list[str] = Field(default="adzuna")
    adzuna_app_id: str = Field(default="")
    adzuna_api_key: str = Field(default="")
    adzuna_base_url: str = Field(default="https://api.adzuna.com/v1/api/jobs")
    adzuna_country: str = Field(default="in")
    job_timeout_seconds: float = Field(default=25.0)
    job_max_retries: int = Field(default=2)
    job_ingestion_enabled: bool = Field(default=True)
    job_refresh_minutes: int = Field(default=30)
    job_refresh_limit: int = Field(default=100)
    job_scheduler_enabled: bool = Field(default=True)
    additional_job_provider_url: str = Field(default="")
    additional_job_provider_api_key: str = Field(default="")

    # Semantic matching weights (sum should be 1.0)
    semantic_weight: float = Field(default=0.40)
    required_skill_weight: float = Field(default=0.30)
    preferred_skill_weight: float = Field(default=0.05)
    experience_weight: float = Field(default=0.10)
    education_weight: float = Field(default=0.05)
    project_weight: float = Field(default=0.10)
    min_match_score: float = Field(default=0.0)
    max_match_score: float = Field(default=100.0)

    # Career readiness weights, configurable and sum to 1.0
    career_technical_weight: float = Field(default=0.30)
    career_project_weight: float = Field(default=0.15)
    career_experience_weight: float = Field(default=0.15)
    career_resume_weight: float = Field(default=0.15)
    career_industry_weight: float = Field(default=0.15)
    career_role_weight: float = Field(default=0.10)

    # Gemini API settings for roadmap guidance
    gemini_api_key: str = Field(default="")
    # The previous default (gemini-3.6-flash) is not a published API model.
    gemini_model: str = Field(default="gemini-3.8-flash")
    gemini_embedding_model: str = Field(default="gemini-embedding-001")
    semantic_embedding_enabled: bool = Field(default=True)
    gemini_base_url: str = Field(default="https://generativelanguage.googleapis.com/v1beta")
    gemini_timeout_seconds: float = Field(default=20.0)
    gemini_max_retries: int = Field(default=2)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return [str(value)]

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_value(cls, value: Any) -> bool:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "false", "0", "no", "off"}:
                return False
            if normalized in {"debug", "development", "true", "1", "yes", "on"}:
                return True
        return value

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.environment.lower() == "production":
            if not self.jwt_secret_key or not self.jwt_secret_key.strip():
                raise ValueError("JWT_SECRET_KEY must be configured for production deployments.")
            if self.debug:
                raise ValueError("DEBUG must be disabled in production.")
            if self.docs_url is not None:
                self.docs_url = None
            if self.openapi_url is not None:
                self.openapi_url = None
            self.allow_credentials = True
            if self.database_url.startswith("sqlite"):
                raise ValueError("DATABASE_URL must point to a managed database in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
