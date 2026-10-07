from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    status: Literal["connected", "unavailable"]
    message: str


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    version: str
    environment: str
    database: DatabaseHealth
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
