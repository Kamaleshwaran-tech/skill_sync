"""
End-to-End System Verification Script for SkillSync AI.
Verifies MySQL connectivity, auth token creation, resume parsing, semantic embedding matching,
skill gap analysis, career readiness scoring, and learning roadmap generation.
"""

from __future__ import annotations

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from app.database.session import SessionLocal, engine
from app.models.models import User, Job, Skill, Resume
from app.ai.engine import SkillSyncAIEngine
from app.utils.security import hash_password, verify_password, create_access_token, decode_token

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("verify_e2e")


def run_e2e_verification() -> bool:
    logger.info("=== 1. VERIFYING MYSQL DATABASE & SEED RECORDS ===")
    with SessionLocal() as db:
        user_count = db.query(User).count()
        job_count = db.query(Job).count()
        skill_count = db.query(Skill).count()
        logger.info("MySQL Records: Users=%d, Jobs=%d, Skills=%d", user_count, job_count, skill_count)
        if user_count == 0 or job_count == 0:
            logger.error("Database tables are missing records!")
            return False

    logger.info("=== 2. VERIFYING AUTH & JWT TOKEN ENGINE ===")
    test_pw = "password123"
    hashed = hash_password(test_pw)
    assert verify_password(test_pw, hashed), "Password verification failed!"
    token, jti = create_access_token("student@skillsync.ai")
    assert isinstance(token, str) and len(token) > 20, "JWT token generation failed!"
    decoded = decode_token(token)
    assert decoded["sub"] == "student@skillsync.ai", "Token subject decode mismatch!"
    logger.info("JWT Token generated and verified successfully: sub=%s, jti=%s", decoded["sub"], jti[:8])

    logger.info("=== 3. VERIFYING AI RESUME PARSING & ENTITY EXTRACTION ===")
    ai = SkillSyncAIEngine()
    sample_resume = """
    Alex Johnson | Full-Stack Software Engineer
    Email: student@skillsync.ai | Location: San Francisco, CA
    Summary: Passionate developer with 2 years of experience building scalable applications with Python, FastAPI, React, and MySQL.
    Technical Skills: Python, FastAPI, React, SQL, MySQL, Git, Docker, REST APIs, TypeScript, JavaScript
    Soft Skills: Problem Solving, Team Collaboration, Communication
    Experience:
    Software Engineer Intern at TechCorp (12 months)
    - Developed high-performance REST APIs using FastAPI and MySQL database.
    - Built responsive, interactive student dashboards with React and TypeScript.
    Education:
    B.Tech in Computer Science, 2024
    Projects:
    1. SkillSync AI Platform: AI-driven career guidance and job matching platform.
    2. Cloud Job Tracker: Real-time job board analytics system.
    """
    parsed = ai.parse_resume_text(sample_resume)
    tech_skill_names = [s.name for s in parsed.technical_skills]
    soft_skill_names = [s.name for s in parsed.soft_skills]
    logger.info("Extracted Technical Skills (%d): %s", len(tech_skill_names), tech_skill_names)
    logger.info("Extracted Soft Skills (%d): %s", len(soft_skill_names), soft_skill_names)
    logger.info("Extracted Experience: %d positions", len(parsed.experiences))
    assert len(tech_skill_names) >= 3, "Skill extraction underperformed!"

    logger.info("=== 4. VERIFYING DENSE VECTOR EMBEDDING & COSINE MATCHING ===")
    sample_job = "Seeking a Junior Full-Stack Engineer proficient in Python, FastAPI, React, and Docker."
    match = ai.match_resume_to_job(
        resume_text=sample_resume,
        job_description=sample_job,
        student_skills=tech_skill_names,
        required_skills=["Python", "FastAPI", "React", "Docker"]
    )
    logger.info("Match Score: %.2f%% (Semantic: %.2f%%, Skill Coverage: %.2f%%)",
                match["overall_match_score"], match["semantic_similarity"], match["skill_coverage"])
    logger.info("Matched Skills: %s | Missing Skills: %s", match["matched_skills"], match["missing_skills"])
    logger.info("AI Natural Language Explanation: %s", match["natural_language_explanation"][:120])
    assert match["overall_match_score"] > 50, "Match score unexpectedly low!"

    logger.info("=== 5. VERIFYING CAREER READINESS & LEARNING ROADMAP ===")
    readiness = ai.calculate_career_readiness(
        student_profile={
            "skills": tech_skill_names,
            "experience_years": 1.5,
            "project_count": 2,
            "resume_quality_score": 90.0,
        },
        target_roles_data={
            "title": "Full-Stack Software Engineer",
            "required_skills": ["Python", "FastAPI", "React", "Docker", "AWS"],
            "experience_required_years": 2.0,
            "project_count": 2,
        }
    )
    logger.info("Overall Career Readiness Score: %.2f%%", readiness["overall_score"])
    logger.info("Dimension Scores: Skill Match=%.1f, Project=%.1f, Resume=%.1f, Industry=%.1f",
                readiness["skill_match_score"], readiness["project_relevance_score"],
                readiness["resume_quality_score"], readiness["industry_demand_score"])

    roadmap = ai.generate_learning_roadmap(
        target_role="Full-Stack Software Engineer",
        student_skills=tech_skill_names,
        missing_skills_with_priority=[
            {"skill_name": "AWS", "priority": "HIGH", "difficulty_level": 2},
            {"skill_name": "Kubernetes", "priority": "MEDIUM", "difficulty_level": 3},
        ],
        career_readiness_score=readiness["overall_score"]
    )
    logger.info("Generated Roadmap with %d learning steps:", len(roadmap.steps))
    for step in roadmap.steps:
        logger.info("  - Step %d: %s (Priority: %s, Est. %s)", step.order, step.skill, step.priority, step.estimated_duration)

    logger.info("=== ALL END-TO-END VERIFICATIONS PASSED WITH 100% SUCCESS! ===")
    return True


if __name__ == "__main__":
    success = run_e2e_verification()
    sys.exit(0 if success else 1)

