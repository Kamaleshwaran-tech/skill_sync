from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import BaseModel


class NormalizedSkill(BaseModel):
    canonical_name: str
    category: str
    aliases: List[str]
    confidence: float = 1.0


class SkillNormalizerInterface(ABC):
    """Abstract interface for skill normalization against a master taxonomy."""

    @abstractmethod
    def normalize(self, raw_skill: str) -> Optional[NormalizedSkill]:
        """Normalize a single raw skill string to its taxonomy canonical name."""
        pass

    @abstractmethod
    def normalize_many(self, raw_skills: List[str]) -> List[NormalizedSkill]:
        """Normalize a list of raw skill strings."""
        pass

    @abstractmethod
    def get_taxonomy(self) -> Dict[str, Dict[str, str]]:
        """Return the active master skill taxonomy."""
        pass
