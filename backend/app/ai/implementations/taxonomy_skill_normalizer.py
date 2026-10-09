from __future__ import annotations

from typing import Dict, List, Optional
from app.ai.interfaces.skill_normalizer import NormalizedSkill, SkillNormalizerInterface
from app.utils.skill_taxonomy import normalize_skill, MASTER_SKILLS, VARIATIONS

SKILL_CATEGORIES: Dict[str, str] = {
    "React": "Frontend",
    "HTML": "Frontend",
    "CSS": "Frontend",
    "TypeScript": "Frontend",
    "Node.js": "Backend",
    "Express.js": "Backend",
    "Django": "Backend",
    "Flask": "Backend",
    "Python": "Programming Languages",
    "Java": "Programming Languages",
    "C++": "Programming Languages",
    "C#": "Programming Languages",
    "MongoDB": "Database",
    "PostgreSQL": "Database",
    "MySQL": "Database",
    "Redis": "Database",
    "Docker": "DevOps & Cloud",
    "AWS": "DevOps & Cloud",
    "Kubernetes": "DevOps & Cloud",
    "Git": "Tools & DevOps",
    "GraphQL": "API & Backend",
}


class TaxonomySkillNormalizer(SkillNormalizerInterface):
    """Normalizes raw skill strings against a structured master taxonomy."""

    def __init__(self, categories: Optional[Dict[str, str]] = None):
        self.categories = categories or SKILL_CATEGORIES
        self.master_skills = MASTER_SKILLS
        self.variations = VARIATIONS

    def normalize(self, raw_skill: str) -> Optional[NormalizedSkill]:
        if not raw_skill:
            return None

        canonical = normalize_skill(raw_skill)
        if not canonical:
            return None

        category = self.categories.get(canonical, "General Technical")
        aliases = [v for v, c in self.variations.items() if c == canonical]

        return NormalizedSkill(
            canonical_name=canonical,
            category=category,
            aliases=aliases,
            confidence=0.95 if raw_skill.strip().lower() in aliases or raw_skill.strip().lower() == canonical.lower() else 0.85,
        )

    def normalize_many(self, raw_skills: List[str]) -> List[NormalizedSkill]:
        normalized_map: Dict[str, NormalizedSkill] = {}
        for raw in raw_skills:
            norm = self.normalize(raw)
            if norm and norm.canonical_name not in normalized_map:
                normalized_map[norm.canonical_name] = norm
        return list(normalized_map.values())

    def get_taxonomy(self) -> Dict[str, Dict[str, str]]:
        taxonomy = {}
        for skill in self.master_skills:
            category = self.categories.get(skill, "General Technical")
            aliases = [v for v, c in self.variations.items() if c == skill]
            taxonomy[skill] = {
                "category": category,
                "aliases": ", ".join(aliases),
            }
        return taxonomy
