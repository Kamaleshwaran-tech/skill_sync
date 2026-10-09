from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProcessedJob(BaseModel):
    external_id: str
    title: str
    company: str
    location: str
    description: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_required_years: float = 0.0
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    url: Optional[str] = None
    source_name: str = "External API"


class JobFetcherInterface(ABC):
    """Abstract interface for fetching and preprocessing external job descriptions."""

    @abstractmethod
    def fetch_jobs(self, query: str, location: Optional[str] = None, limit: int = 10) -> List[ProcessedJob]:
        """Fetch live job postings from an external API or source."""
        pass

    @abstractmethod
    def preprocess_job(self, raw_job: Dict[str, Any]) -> ProcessedJob:
        """Clean, normalize, and extract skill requirements from a raw job payload."""
        pass
