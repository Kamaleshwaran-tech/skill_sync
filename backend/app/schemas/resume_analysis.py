from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class ResumeAnalysisOut(BaseModel):
    id: int
    resume_id: int
    profile: Optional[Any]
    confidence: Optional[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
