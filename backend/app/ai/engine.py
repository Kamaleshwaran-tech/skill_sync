from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.ai.implementations.api_job_fetcher import ApiJobFetcher
from app.ai.implementations.career_readiness_engine import CareerReadinessEngine
from app.ai.implementations.gemini_llm_provider import GeminiLLMProvider
from app.ai.implementations.learning_roadmap_generator import LearningRoadmapGenerator
from app.ai.implementations.pdf_docx_resume_parser import PdfDocxResumeParser
from app.ai.implementations.priority_skill_gap_analyzer import PrioritySkillGapAnalyzer
from app.ai.implementations.rule_recommendation_engine import RuleRecommendationEngine
from app.ai.implementations.taxonomy_skill_normalizer import TaxonomySkillNormalizer
from app.services.semantic_job_matching import SemanticJobMatchingService


class SkillSyncAIEngine:
    """Compatibility facade for deterministic NLP analysis and Gemini guidance."""

    def __init__(self, resume_parser=None, skill_normalizer=None, job_fetcher=None, scoring_engine=None,
                 skill_gap_analyzer=None, roadmap_generator=None, recommendation_engine=None, llm_provider=None):
        self.resume_parser = resume_parser or PdfDocxResumeParser()
        self.skill_normalizer = skill_normalizer or TaxonomySkillNormalizer()
        self.job_fetcher = job_fetcher or ApiJobFetcher()
        self.scoring_engine = scoring_engine or CareerReadinessEngine()
        self.skill_gap_analyzer = skill_gap_analyzer or PrioritySkillGapAnalyzer()
        self.roadmap_generator = roadmap_generator or LearningRoadmapGenerator()
        self.recommendation_engine = recommendation_engine or RuleRecommendationEngine()
        self.llm_provider = llm_provider or GeminiLLMProvider()
        self.matcher = SemanticJobMatchingService()

    def parse_resume_file(self, file_path: str, file_type: str): return self.resume_parser.parse_file(file_path, file_type)
    def parse_resume_text(self, text: str): return self.resume_parser.parse_text(text)
    def normalize_skill(self, raw_skill: str): return self.skill_normalizer.normalize(raw_skill)
    def normalize_skills(self, raw_skills: List[str]): return self.skill_normalizer.normalize_many(raw_skills)
    def fetch_live_jobs(self, query: str, location: Optional[str] = None, limit: int = 10): return self.job_fetcher.fetch_jobs(query, location, limit)
    def preprocess_job(self, raw_job: Dict[str, Any]): return self.job_fetcher.preprocess_job(raw_job)

    def match_resume_to_job(self, resume_text: str, job_description: str, student_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        result = self.matcher.calculate({"resume_text": resume_text, "skills": student_skills}, {"description": job_description, "required_skills": required_skills})
        result["natural_language_explanation"] = self.llm_provider.explain_match_score(result)
        return result

    def calculate_career_readiness(self, student_profile: Dict[str, Any], target_roles_data: Dict[str, Any]) -> Dict[str, Any]:
        result = self.scoring_engine.calculate_readiness(student_profile, target_roles_data).model_dump()
        result["natural_language_explanation"] = self.llm_provider.explain_career_readiness(result)
        return result

    def identify_skill_gaps(self, student_skills, required_skills, preferred_skills, industry_demand=None):
        return self.skill_gap_analyzer.analyze_gaps(student_skills, required_skills, preferred_skills, industry_demand or {})
    def generate_learning_roadmap(self, target_role, student_skills, missing_skills_with_priority, career_readiness_score=0.0):
        return self.roadmap_generator.generate_roadmap(target_role, student_skills, missing_skills_with_priority, career_readiness_score)
    def recommend_learning_path(self, target_role, missing_skills, current_skills):
        result = self.recommendation_engine.generate_recommendations(target_role, missing_skills, current_skills).model_dump()
        result["target_role"] = target_role
        result["natural_language_explanation"] = self.llm_provider.explain_recommendations(result)
        return result
