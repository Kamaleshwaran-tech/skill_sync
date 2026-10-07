from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None


class ProjectItem(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    skills_used: List[str] = Field(default_factory=list)


class ExperienceItem(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    years: float = 0.0


class ExtractedSkill(BaseModel):
    name: str
    confidence: float = 1.0
    category: Optional[str] = None
    raw_match: Optional[str] = None
    is_soft_skill: bool = False


class ParsedResume(BaseModel):
    name: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    technical_skills: List[ExtractedSkill] = Field(default_factory=list)
    soft_skills: List[ExtractedSkill] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    experiences: List[ExperienceItem] = Field(default_factory=list)
    sections: Dict[str, str] = Field(default_factory=dict)
    raw_text: str = ""
    confidence: float = 1.0


class ResumeParserInterface(ABC):
    """Abstract interface for resume parsing."""

    @abstractmethod
    def parse_file(self, file_path: str, file_type: str) -> ParsedResume:
        """Parse PDF or DOCX resume file and extract structured entities."""
        pass

    @abstractmethod
    def parse_text(self, text: str) -> ParsedResume:
        """Parse raw resume text into structured entities."""
        pass
