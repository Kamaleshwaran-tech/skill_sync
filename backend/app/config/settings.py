from functools import lru_cache
from typing import Literal
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

COUNTRIES = {
    "in": "India",
    "gb": "United Kingdom",
    "us": "United States",
    "au": "Australia",
    "ca": "Canada",
}


class Settings(BaseSettings):
    app_name: str = "SkillSync"
    app_version: str = "0.3.0"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"
    docs_url: str | None = "/api/v1/docs"
    redoc_url: str | None = "/api/v1/redoc"
    openapi_url: str | None = "/api/v1/openapi.json"
    database_url: str = "sqlite:///./skillsync_ai.db"
    db_echo: bool = False
    cors_origins: str | list[str] = "http://localhost:5173,http://127.0.0.1:5173"
    allow_credentials: bool = True
    log_level: str = "INFO"
    rate_limit_per_minute: int = 120
    rate_limit_burst: int = 180
    jwt_secret_key: str = Field(default="", repr=False)
    jwt_algorithm: Literal["HS256"] = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    resume_storage_dir: str = "./storage/resumes"
    resume_max_upload_mb: int = Field(default=5, ge=1, le=10)
    adzuna_app_id: str = ""
    adzuna_api_key: str = Field(default="", repr=False)
    adzuna_country: Literal["in", "gb", "us", "au", "ca"] = "in"
    job_timeout_seconds: float = Field(default=15, ge=1, le=30)
    job_max_retries: int = Field(default=1, ge=0, le=2)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def origins(cls, value):
        return (
            [x.strip() for x in value.split(",") if x.strip()]
            if isinstance(value, str)
            else value
        )

    @model_validator(mode="after")
    def security(self):
        if (
            len(self.jwt_secret_key) < 32
            or len(set(self.jwt_secret_key)) < 8
            or "REPLACE_" in self.jwt_secret_key
            or self.jwt_secret_key
            == "skillsync-super-secure-jwt-secret-key-32-chars-long"
        ):
            raise ValueError(
                "Configure a unique random JWT_SECRET_KEY of at least 32 characters. For an existing .env see README.md; setup preserves existing secrets."
            )
        if self.environment == "production":
            self.debug = False
            self.docs_url = self.redoc_url = self.openapi_url = None
        return self


@lru_cache
def get_settings():
    return Settings()
