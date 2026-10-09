from __future__ import annotations

from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config.settings import get_settings
from app.services.semantic_embedding import GeminiEmbeddingService
from app.utils.skill_taxonomy import normalize_skill


class SemanticJobMatchingService:
    """Deterministic, explainable job matching using TF-IDF and skill coverage."""

    def __init__(self, weights: dict[str, float] | None = None):
        settings = get_settings()
        defaults = {
            "text": settings.semantic_weight,
            "required_skill": settings.required_skill_weight,
            "preferred_skill": settings.preferred_skill_weight,
            "experience": settings.experience_weight,
            "education": settings.education_weight,
            "project": settings.project_weight,
        }
        self.weights = {**defaults, **(weights or {})}
        self.embedding_service = GeminiEmbeddingService()

    def calculate(self, student_profile: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
        student_skills = self._skill_set(student_profile.get("skills", []))
        required_skills = self._skill_set(job.get("required_skills", []))
        preferred_skills = self._skill_set(job.get("preferred_skills", []))
        required_match, preferred_match = student_skills & required_skills, student_skills & preferred_skills
        required_missing, preferred_missing = sorted(required_skills - student_skills), sorted(preferred_skills - student_skills)
        resume_text = self._to_text(student_profile.get("resume_text", ""))
        job_text = self._to_text(job.get("description", ""))
        lexical_similarity = self._text_similarity(resume_text, job_text)
        embedding_similarity = self.embedding_service.similarity(resume_text, job_text)
        # Gemini embeddings improve semantic recall when configured.  The local
        # TF-IDF score keeps matching deterministic and available offline.
        text_similarity = embedding_similarity if embedding_similarity is not None else lexical_similarity
        required_coverage, preferred_coverage = self._coverage(required_match, required_skills), self._coverage(preferred_match, preferred_skills)
        experience_relevance = self._experience_relevance(student_profile.get("experience_years", 0), job.get("experience_required_years", 0))
        education_compatibility = self._education_compatibility(student_profile.get("education", []), job.get("education_required", []))
        project_relevance = self._project_relevance(student_profile.get("project_count", 0), job.get("project_count", 0))
        score = sum((
            text_similarity * self.weights["text"], required_coverage * self.weights["required_skill"],
            preferred_coverage * self.weights["preferred_skill"], experience_relevance * self.weights["experience"],
            education_compatibility * self.weights["education"], project_relevance * self.weights["project"],
        )) * 100
        breakdown = {
            "text_similarity": round(text_similarity * 100, 2),
            "semantic_similarity": round(text_similarity * 100, 2),  # backwards-compatible API key
            "lexical_similarity": round(lexical_similarity * 100, 2),
            "embedding_similarity": round(embedding_similarity * 100, 2) if embedding_similarity is not None else None,
            "required_skill_coverage": round(required_coverage * 100, 2),
            "preferred_skill_coverage": round(preferred_coverage * 100, 2),
            "experience_relevance": round(experience_relevance * 100, 2),
            "education_compatibility": round(education_compatibility * 100, 2),
            "project_relevance": round(project_relevance * 100, 2),
        }
        return {
            "overall_match_score": round(max(0.0, min(100.0, score)), 2), **breakdown,
            "matched_skills": self._display_skills(required_match | preferred_match), "missing_skills": self._display_skills(set(required_missing + preferred_missing)),
            "required_missing_skills": self._display_skills(set(required_missing)), "preferred_missing_skills": self._display_skills(set(preferred_missing)),
            "strengths": self._strengths(required_match, preferred_match, text_similarity),
            "potential_concerns": self._concerns(self._display_skills(set(required_missing)), self._display_skills(set(preferred_missing)), experience_relevance, education_compatibility),
            "score_breakdown": breakdown,
        }

    def _text_similarity(self, left: str, right: str) -> float:
        if not left.strip() or not right.strip(): return 0.0
        try: matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform([left, right])
        except ValueError: return 0.0
        return float(max(0.0, min(1.0, cosine_similarity(matrix[0], matrix[1])[0][0])))

    def _skill_set(self, skills: Any) -> set[str]:
        normalized = set()
        for skill in skills or []:
            value = str(skill).strip()
            if value: normalized.add((normalize_skill(value) or value).strip().lower())
        return normalized

    def _display_skills(self, skills: set[str]) -> list[str]:
        return sorted(normalize_skill(skill) or skill for skill in skills)

    def _coverage(self, matched: set[str], required: set[str]) -> float: return len(matched) / len(required) if required else 1.0
    def _experience_relevance(self, student: Any, required: Any) -> float:
        required, student = max(float(required or 0), 0.0), max(float(student or 0), 0.0)
        return 1.0 if required == 0 else min(1.0, student / required)
    def _education_compatibility(self, student: Any, required: Any) -> float:
        requirements = {str(item).strip().lower() for item in required or [] if str(item).strip()}
        return 1.0 if not requirements or any(term in self._to_text(student).lower() for term in requirements) else 0.0
    def _project_relevance(self, student: Any, required: Any) -> float:
        required, student = max(int(required or 0), 0), max(int(student or 0), 0)
        return 1.0 if required == 0 else min(1.0, student / required)
    def _to_text(self, value: Any) -> str:
        return value if isinstance(value, str) else " ".join(map(str, value or [])) if isinstance(value, (list, tuple, set)) else str(value or "")
    def _strengths(self, required: set[str], preferred: set[str], text: float) -> list[str]:
        strengths = []
        if required: strengths.append(f"Required skills matched: {', '.join(self._display_skills(required)[:3])}")
        if preferred: strengths.append(f"Preferred skills matched: {', '.join(self._display_skills(preferred)[:3])}")
        if text >= .25: strengths.append("Resume language has meaningful semantic overlap with this job description")
        return strengths or ["No strong match signals were identified yet"]
    def _concerns(self, required: list[str], preferred: list[str], experience: float, education: float) -> list[str]:
        concerns = []
        if required: concerns.append(f"Missing required skills: {', '.join(required[:3])}")
        if preferred: concerns.append(f"Missing preferred skills: {', '.join(preferred[:3])}")
        if experience < .75: concerns.append("Relevant experience is below the role requirement")
        if education == 0: concerns.append("The listed education does not show the job's stated requirement")
        return concerns or ["No material skill or qualification gaps detected"]
