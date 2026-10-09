from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.models import Job, JobMatch, Skill, User, UserSkill
from app.repositories.job_match_repository import JobMatchRepository
from app.services.semantic_job_matching import SemanticJobMatchingService


def test_semantic_matching_service_returns_match_breakdown():
    service = SemanticJobMatchingService()
    service.embedding_service.settings.semantic_embedding_enabled = False

    student_profile = {
        "skills": ["Python", "React", "Node.js", "Docker"],
        "experience_years": 2,
        "project_count": 3,
        "resume_text": "Python developer with React and Node.js projects",
    }
    job = {
        "title": "Full Stack Developer",
        "description": "Build web applications using React, Node.js, PostgreSQL, and Docker.",
        "required_skills": ["React", "Node.js", "PostgreSQL", "Docker"],
        "preferred_skills": ["AWS"],
        "experience_required_years": 2,
        "project_count": 2,
    }

    result = service.calculate(student_profile, job)

    assert 0 <= result["overall_match_score"] <= 100
    assert "React" in result["matched_skills"]
    assert "Node.js" in result["matched_skills"]
    assert "Docker" in result["matched_skills"]
    assert "PostgreSQL" in result["required_missing_skills"]
    assert "AWS" in result["preferred_missing_skills"]
    assert "score_breakdown" in result
    assert result["text_similarity"] > 0
    assert result["education_compatibility"] == 100
    assert result["embedding_similarity"] is None


def test_job_match_repository_persists_match_and_skill_gaps():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(email="student@example.com", hashed_password="hashed", full_name="Student User", role="STUDENT")
    session.add(user)
    session.commit()
    session.refresh(user)

    skill = Skill(name="PostgreSQL", category="technical")
    session.add(skill)
    session.commit()
    session.refresh(skill)

    user_skill = UserSkill(user_id=user.id, skill_id=skill.id, proficiency=2, source="resume")
    session.add(user_skill)
    session.commit()

    job = Job(title="Backend Developer", company="Acme", location="Remote", job_type="Full-time")
    session.add(job)
    session.commit()
    session.refresh(job)

    result = {
        "overall_match_score": 82.5,
        "matched_skills": ["React", "Python"],
        "missing_skills": ["PostgreSQL"],
        "required_missing_skills": ["PostgreSQL"],
        "preferred_missing_skills": [],
        "strengths": ["Strong alignment on required skills"],
        "potential_concerns": ["Missing required skills: PostgreSQL"],
        "semantic_similarity": 75.0,
        "required_skill_coverage": 60.0,
        "preferred_skill_coverage": 0.0,
        "experience_relevance": 80.0,
        "project_relevance": 90.0,
        "score_breakdown": {
            "semantic_similarity": 75.0,
            "required_skill_coverage": 60.0,
            "preferred_skill_coverage": 0.0,
            "experience_relevance": 80.0,
            "project_relevance": 90.0,
        },
    }

    repository = JobMatchRepository(session)
    match_row = repository.save_match(user.id, job.id, result)

    assert match_row.id is not None
    assert match_row.match_score == 82.5
    assert match_row.skill_gaps
    assert any(gap.skill.name == "PostgreSQL" for gap in match_row.skill_gaps)

    session.close()
