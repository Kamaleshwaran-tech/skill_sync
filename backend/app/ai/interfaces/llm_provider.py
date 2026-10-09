from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class LLMExplanationProviderInterface(ABC):
    """Abstract interface for LLM explanation generation (Gemini / OpenAI).

    NOTE: All similarity matching and score calculations MUST remain deterministic and TF-IDF/skill-rule based.
    The LLM is strictly used to translate deterministic metrics into natural language explanations.
    """

    @abstractmethod
    def explain_match_score(self, match_data: Dict[str, Any]) -> str:
        """Generate a natural language explanation of a job match score."""
        pass

    @abstractmethod
    def explain_career_readiness(self, readiness_data: Dict[str, Any]) -> str:
        """Generate a natural language explanation of a Career Readiness score."""
        pass

    @abstractmethod
    def explain_recommendations(self, recommendation_data: Dict[str, Any]) -> str:
        """Generate a natural language explanation of learning recommendations."""
        pass

    @abstractmethod
    def enhance_roadmap_advice(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance roadmap advice and descriptions with natural language explanations."""
        pass
