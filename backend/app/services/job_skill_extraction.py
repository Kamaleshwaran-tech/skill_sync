from __future__ import annotations

import re
from typing import Any

from app.utils.skill_taxonomy import MASTER_SKILLS, normalize_skill

SOFT_SKILLS = {
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "analytical thinking",
    "adaptability",
    "time management",
    "collaboration",
    "presentation",
    "creativity",
    "ownership",
    "mentoring",
    "documentation",
    "empathy",
}

REQUIRED_HINTS = {
    "required",
    "must",
    "strong",
    "experience with",
    "proficiency in",
    "expertise in",
    "working knowledge of",
    "hands-on",
    "minimum",
    "ability to",
}

PREFERRED_HINTS = {
    "preferred",
    "nice to have",
    "plus",
    "bonus",
    "advantage",
    "good to have",
}


class JobSkillExtractionService:
    def extract(self, title: str, description: str) -> dict[str, list[str]]:
        text = f"{title} {description}"
        cleaned = re.sub(r"\s+", " ", text or "").strip()
        lower = cleaned.lower()

        required = self._extract_type(cleaned, REQUIRED_HINTS, "required")
        preferred = self._extract_type(cleaned, PREFERRED_HINTS, "preferred")
        soft_skills = self._extract_soft_skills(cleaned)

        # Any anatomy not explicitly marked goes into required by default for core technical skills.
        # This prevents missing high-confidence skills while keeping preferred/required separation explicit.
        explicit_required = set(required)
        explicit_preferred = set(preferred)
        soft = set(soft_skills)

        for skill in MASTER_SKILLS:
            if skill.lower() in lower:
                if skill not in explicit_required and skill not in explicit_preferred and skill not in soft:
                    explicit_required.add(skill)

        return {
            "required": sorted(explicit_required),
            "preferred": sorted(explicit_preferred),
            "soft_skills": sorted(soft),
        }

    def _extract_type(self, text: str, hints: set[str], skill_type: str) -> set[str]:
        items: set[str] = set()
        sentences = re.split(r"[.;\n]", text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if not any(hint in sentence_lower for hint in hints):
                continue
            for candidate in re.split(r"[,/|]", sentence):
                normalized = normalize_skill(candidate)
                if normalized:
                    items.add(normalized)
        return items

    def _extract_soft_skills(self, text: str) -> set[str]:
        hits: set[str] = set()
        lower = text.lower()
        for skill in SOFT_SKILLS:
            if skill in lower:
                hits.add(skill.title())
        return hits
