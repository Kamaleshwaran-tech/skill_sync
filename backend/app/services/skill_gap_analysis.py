from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Any


class SkillGapAnalysisService:
    """Deterministic skill gap analysis for recommended jobs."""

    def analyze_jobs(
        self,
        student_skills: list[str | dict[str, Any]] | None,
        jobs: list[dict[str, Any]] | None,
        job_market_demand: dict[str, float] | None = None,
        prerequisites: dict[str, list[str]] | None = None,
    ) -> list[dict[str, Any]]:
        current_skill_map, current_display_map = self._to_proficiency_map(student_skills or [])
        market_demand = self._normalize_market_demand(job_market_demand or {})
        prereq_map = self._normalize_prerequisites(prerequisites or {})

        results: list[dict[str, Any]] = []
        for job in jobs or []:
            job_name = str(job.get("title") or job.get("name") or "Target Role")
            required_entries = self._normalize_skill_entries(job.get("required_skills", []))
            preferred_entries = self._normalize_skill_entries(job.get("preferred_skills", []))
            required_normalized = [entry["normalized_name"] for entry in required_entries]
            preferred_normalized = [entry["normalized_name"] for entry in preferred_entries]
            required_names = [entry["name"] for entry in required_entries]
            preferred_names = [entry["name"] for entry in preferred_entries]

            current_names = sorted(current_display_map.values())
            matched_norms = set(current_skill_map) & set(required_normalized)
            missing_norms = set(required_normalized) - set(current_skill_map)
            preferred_missing_norms = set(preferred_normalized) - set(current_skill_map)
            matched_skills = sorted({current_display_map.get(norm, self._display_skill_name(norm)) for norm in matched_norms})
            missing_skills = sorted({next(entry["name"] for entry in required_entries if entry["normalized_name"] == norm) for norm in missing_norms})
            preferred_missing = sorted({next(entry["name"] for entry in preferred_entries if entry["normalized_name"] == norm) for norm in preferred_missing_norms})

            gaps = self._build_gap_details(
                missing_skills=sorted(missing_norms),
                preferred_missing=sorted(preferred_missing_norms),
                current_skill_map=current_skill_map,
                market_demand=market_demand,
                prerequisites=prereq_map,
                required_entries=required_entries,
                preferred_entries=preferred_entries,
            )

            results.append(
                {
                    "jobTitle": job_name,
                    "currentSkills": current_names,
                    "requiredSkills": required_names,
                    "matchedSkills": matched_skills,
                    "missingSkills": missing_skills,
                    "preferredMissingSkills": preferred_missing,
                    "gaps": gaps,
                }
            )

        return results

    def _build_gap_details(
        self,
        missing_skills: list[str],
        preferred_missing: list[str],
        current_skill_map: dict[str, float],
        market_demand: dict[str, float],
        prerequisites: dict[str, list[str]],
        required_entries: list[dict[str, Any]],
        preferred_entries: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        required_lookup = {entry["normalized_name"]: entry for entry in required_entries}
        preferred_lookup = {entry["normalized_name"]: entry for entry in preferred_entries}

        missing_items = []
        for skill in missing_skills:
            entry = required_lookup.get(skill, {})
            display_name = entry.get("name") or self._display_skill_name(skill)
            missing_items.append(
                {
                    "skill": display_name,
                    "normalized_name": skill,
                    "kind": "required",
                    "currentProficiency": float(current_skill_map.get(skill, 0.0)),
                    "requiredProficiency": float(entry.get("proficiency", 3.0)),
                    "gap": self._calculate_gap(current_skill_map.get(skill, 0.0), entry.get("proficiency", 3.0)),
                    "industryDemand": float(market_demand.get(skill, 0.5)),
                    "priority": self._priority_for(skill, True, market_demand.get(skill, 0.5), prerequisites),
                }
            )
        for skill in preferred_missing:
            entry = preferred_lookup.get(skill, {})
            display_name = entry.get("name") or self._display_skill_name(skill)
            missing_items.append(
                {
                    "skill": display_name,
                    "normalized_name": skill,
                    "kind": "preferred",
                    "currentProficiency": float(current_skill_map.get(skill, 0.0)),
                    "requiredProficiency": float(entry.get("proficiency", 2.0)),
                    "gap": self._calculate_gap(current_skill_map.get(skill, 0.0), entry.get("proficiency", 2.0)),
                    "industryDemand": float(market_demand.get(skill, 0.35)),
                    "priority": self._priority_for(skill, False, market_demand.get(skill, 0.35), prerequisites),
                }
            )

        for item in missing_items:
            item["reason"] = self._describe_priority(
                normalized_skill=item["normalized_name"],
                display_skill=item["skill"],
                kind=item["kind"],
                score=item["priority"],
                industry_demand=item["industryDemand"],
                prerequisites=prerequisites,
            )
            item["recommendedOrder"] = 0

        ordered = sorted(
            missing_items,
            key=lambda x: (
                self._priority_rank(x["priority"]),
                0 if x["kind"] == "required" else 1,
                -float(x["industryDemand"]),
                -float(x["gap"]),
            ),
            reverse=True,
        )

        for index, item in enumerate(ordered, start=1):
            item["recommendedOrder"] = index
            item["priority"] = self._priority_label(item["priority"])
            item["industryDemand"] = round(float(item["industryDemand"]), 2)
            item["gap"] = round(float(item["gap"]), 2)
            item["currentProficiency"] = round(float(item["currentProficiency"]), 2)
            item["requiredProficiency"] = round(float(item["requiredProficiency"]), 2)
            item.pop("normalized_name", None)

        return ordered

    def _priority_for(
        self,
        skill: str,
        is_required: bool,
        industry_demand: float,
        prerequisites: dict[str, list[str]],
    ) -> float:
        mandatory = 1.0 if is_required else 0.45
        demand_score = self._clamp(industry_demand, 0.0, 1.0)
        relevance = 1.0 if is_required else 0.6
        prerequisite_score = 1.0 if skill in prerequisites else 0.0
        if skill in prerequisites:
            prerequisite_score = 1.0
        else:
            prerequisite_score = 0.0
        for prereq_list in prerequisites.values():
            if skill in prereq_list:
                prerequisite_score = max(prerequisite_score, 0.7)
        score = (mandatory * 0.45) + (demand_score * 0.25) + (relevance * 0.20) + (prerequisite_score * 0.10)
        return self._clamp(score, 0.0, 1.0)

    def _priority_label(self, score: float) -> str:
        if score >= 0.75:
            return "HIGH"
        if score >= 0.45:
            return "MEDIUM"
        return "LOW"

    def _priority_rank(self, level: str | float) -> int:
        if isinstance(level, str):
            normalized = level.upper()
            return {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(normalized, 0)
        return self._priority_rank(self._priority_label(level))

    def _describe_priority(
        self,
        normalized_skill: str,
        display_skill: str,
        kind: str,
        score: float,
        industry_demand: float,
        prerequisites: dict[str, list[str]],
    ) -> str:
        label = self._priority_label(score)
        parts = []
        if kind == "required":
            parts.append("mandatory skill")
        else:
            parts.append("recommended skill")
        if normalized_skill in prerequisites or any(normalized_skill in values for values in prerequisites.values()):
            parts.append("prerequisite dependency")
        if industry_demand >= 0.7:
            parts.append("strong market demand")
        elif industry_demand >= 0.4:
            parts.append("moderate market demand")
        else:
            parts.append("lower market demand")
        return f"{display_skill} is a {label.lower()} priority because it is a {' and '.join(parts)}."

    def _normalize_market_demand(self, demand_map: dict[str, float]) -> dict[str, float]:
        normalized: dict[str, float] = {}
        for key, value in demand_map.items():
            normalized[self._normalize_skill_name(str(key))] = self._clamp(float(value), 0.0, 1.0)
        return normalized

    def _normalize_prerequisites(self, prerequisites: dict[str, list[str]]) -> dict[str, list[str]]:
        normalized: dict[str, list[str]] = {}
        for key, values in prerequisites.items():
            normalized[self._normalize_skill_name(str(key))] = [self._normalize_skill_name(str(value)) for value in values]
        return normalized

    def _to_proficiency_map(self, skills: list[str | dict[str, Any]]) -> tuple[dict[str, float], dict[str, str]]:
        proficiency_map: dict[str, float] = {}
        display_map: dict[str, str] = {}
        for item in skills:
            if hasattr(item, "model_dump"):
                item = item.model_dump()
            if isinstance(item, str):
                normalized = self._normalize_skill_name(item)
                proficiency_map[normalized] = 3.0
                display_map[normalized] = self._display_skill_name(item)
            elif isinstance(item, dict):
                name = item.get("name") or item.get("skill")
                if name is None:
                    continue
                normalized = self._normalize_skill_name(str(name))
                proficiency_map[normalized] = float(item.get("proficiency", item.get("level", 3.0)))
                display_map[normalized] = self._display_skill_name(str(name))
        return proficiency_map, display_map

    def _normalize_skill_entries(self, items: list[str | dict[str, Any]]) -> list[dict[str, Any]]:
        values: list[dict[str, Any]] = []
        for item in items:
            if hasattr(item, "model_dump"):
                item = item.model_dump()
            if isinstance(item, str):
                display_name = self._display_skill_name(item)
                normalized = self._normalize_skill_name(item)
                values.append({"name": display_name, "normalized_name": normalized, "proficiency": 3.0})
            elif isinstance(item, dict):
                name = item.get("name") or item.get("skill")
                if not name:
                    continue
                display_name = self._display_skill_name(str(name))
                normalized = self._normalize_skill_name(str(name))
                values.append({
                    "name": display_name,
                    "normalized_name": normalized,
                    "proficiency": float(item.get("proficiency", item.get("level", 3.0))),
                })
        return values

    def _display_skill_name(self, value: str) -> str:
        cleaned = str(value).strip()
        mapping = {
            "node.js": "Node.js",
            "nodejs": "Node.js",
            "postgresql": "PostgreSQL",
            "aws": "AWS",
            "docker": "Docker",
            "python": "Python",
            "react": "React",
            "javascript": "JavaScript",
            "sql": "SQL",
            "kubernetes": "Kubernetes",
            "typescript": "TypeScript",
            "java": "Java",
            "go": "Go",
        }
        lowered = self._normalize_skill_name(cleaned)
        return mapping.get(lowered, cleaned)

    def _normalize_skill_name(self, value: str) -> str:
        if value is None:
            return ""
        normalized = str(value).strip().lower()
        normalized = normalized.replace("_", " ")
        normalized = re.sub(r"\s+", " ", normalized)
        normalized = normalized.replace("react.js", "react")
        normalized = normalized.replace("reactjs", "react")
        normalized = normalized.replace("node.js", "node.js")
        normalized = normalized.replace("postgresql", "postgresql")
        return normalized

    def _calculate_gap(self, current: float, required: float) -> float:
        if required <= 0:
            return 0.0
        return max(0.0, required - current)

    def _clamp(self, value: float, low: float, high: float) -> float:
        return max(low, min(high, float(value)))
