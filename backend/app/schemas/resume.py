from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class BaseConfig:
    model_config = ConfigDict(from_attributes=True)


class ResumeOut(BaseModel):
    id: int
    user_id: int
    filename: str
    file_type: str
    file_size: Optional[int]
    status: str
    is_active: bool
    uploaded_at: datetime

    model_config = BaseConfig.model_config
