from app.ai.engine import SkillSyncAIEngine


def test_engine_uses_tfidf_matching_without_network_access():
    result = SkillSyncAIEngine().match_resume_to_job(
        resume_text="Python developer building REST APIs with PostgreSQL.",
        job_description="Backend developer needed for Python REST API and PostgreSQL work.",
        student_skills=["python", "postgres"],
        required_skills=["Python", "PostgreSQL", "Docker"],
    )
    assert result["text_similarity"] > 0
    assert result["required_skill_coverage"] == 66.67
    assert result["missing_skills"] == ["Docker"]


def test_engine_keeps_rule_based_skill_normalization():
    normalized = SkillSyncAIEngine().normalize_skills(["reactjs", "postgres", "k8s"])
    assert [item.canonical_name for item in normalized] == ["React", "PostgreSQL", "Kubernetes"]
