"""
PostgreSQL Seed Data Script for SkillSync AI.
Populates standard taxonomy skills, companies, jobs with required/preferred skills,
test users (candidate and employer), and learning resources into PostgreSQL.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.database.session import SessionLocal, engine, Base
from app.models.models import (
    User,
    Skill,
    Job,
    JobSkill,
    JobSource,
    Company,
    Course,
    CandidateProfile,
    EmployerProfile,
)
from app.utils.security import hash_password

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_postgres_data")


def seed_initial_data_if_empty(db: Session | None = None) -> bool:
    """Auto-seeds standard taxonomy, benchmark jobs, and courses if the database is unpopulated."""
    close_when_done = False
    if db is None:
        db = SessionLocal()
        close_when_done = True

    try:
        if db.query(Skill).count() > 0:
            return False

        logger.info("Database is empty. Automatically seeding standard taxonomy, benchmark jobs, users, and courses...")
        _perform_seeding(db)
        return True
    except Exception as exc:
        logger.warning("Auto-seeding skipped or failed: %s", exc)
        return False
    finally:
        if close_when_done:
            db.close()


def seed_database():
    logger.info("Ensuring all tables exist...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        _perform_seeding(db)
    finally:
        db.close()


def _perform_seeding(db: Session):
    try:
        # 1. Seed Skills
        skills_data = [
            ("Python", "technical"),
            ("FastAPI", "technical"),
            ("SQL", "technical"),
            ("PostgreSQL", "technical"),
            ("Docker", "technical"),
            ("React", "technical"),
            ("TypeScript", "technical"),
            ("JavaScript", "technical"),
            ("Node.js", "technical"),
            ("AWS", "technical"),
            ("Kubernetes", "technical"),
            ("Machine Learning", "technical"),
            ("PyTorch", "technical"),
            ("Git", "technical"),
            ("CI/CD", "technical"),
            ("REST API", "technical"),
            ("GraphQL", "technical"),
            ("Linux", "technical"),
            ("Problem Solving", "soft"),
            ("Communication", "soft"),
            ("Teamwork", "soft"),
        ]

        skill_map = {}
        for name, category in skills_data:
            existing = db.query(Skill).filter(Skill.name == name).first()
            if not existing:
                skill = Skill(name=name, category=category)
                db.add(skill)
                db.flush()
                skill_map[name] = skill
            else:
                skill_map[name] = existing

        logger.info("Seeded %d taxonomy skills.", len(skill_map))

        # 2. Seed Test Users
        test_candidate = db.query(User).filter(User.email == "student@skillsync.ai").first()
        if not test_candidate:
            test_candidate = User(
                email="student@skillsync.ai",
                hashed_password=hash_password("password123"),
                full_name="Alex Johnson",
                role="CANDIDATE",
                is_active=True,
            )
            db.add(test_candidate)
            db.flush()
            cand_profile = CandidateProfile(
                user_id=test_candidate.id,
                bio="Passionate computer science student focused on full-stack development and AI applications.",
                phone="+1 (555) 234-5678",
                location="San Francisco, CA",
                github_url="https://github.com/alexjohnson",
                linkedin_url="https://linkedin.com/in/alexjohnson",
            )
            db.add(cand_profile)
            logger.info("Created test candidate user: student@skillsync.ai / password123")

        test_employer = db.query(User).filter(User.email == "recruiter@techcorp.com").first()
        if not test_employer:
            test_employer = User(
                email="recruiter@techcorp.com",
                hashed_password=hash_password("password123"),
                full_name="Sarah Miller",
                role="EMPLOYER",
                is_active=True,
            )
            db.add(test_employer)
            db.flush()
            emp_profile = EmployerProfile(
                user_id=test_employer.id,
                position="Technical Talent Lead",
                phone="+1 (555) 987-6543",
            )
            db.add(emp_profile)
            logger.info("Created test employer user: recruiter@techcorp.com / password123")

        # 3. Seed Job Source
        source = db.query(JobSource).filter(JobSource.name == "System Internal").first()
        if not source:
            source = JobSource(name="System Internal", provider="internal", api_url=None)
            db.add(source)
            db.flush()

        # 4. Seed Companies & Jobs
        jobs_data = [
            {
                "title": "Junior Full-Stack Engineer",
                "company": "CloudScale Technologies",
                "location": "San Francisco, CA (Hybrid)",
                "job_type": "Full-time",
                "salary_min": 85000,
                "salary_max": 115000,
                "description": "Build high-performance web applications using React, TypeScript, Python FastAPI, and PostgreSQL. Collaborate with cross-functional teams to design clean REST APIs and cloud services.",
                "required_skills": ["Python", "FastAPI", "React", "SQL", "Git"],
                "preferred_skills": ["Docker", "PostgreSQL", "TypeScript", "AWS"],
            },
            {
                "title": "Backend AI Systems Engineer",
                "company": "NeuralEdge Labs",
                "location": "Remote",
                "job_type": "Full-time",
                "salary_min": 105000,
                "salary_max": 140000,
                "description": "Develop scalable AI inference pipelines and backend microservices using FastAPI, PyTorch, Docker, and PostgreSQL. Experience with vector embeddings and prompt engineering is a plus.",
                "required_skills": ["Python", "FastAPI", "Machine Learning", "Docker", "REST API"],
                "preferred_skills": ["PyTorch", "PostgreSQL", "Kubernetes", "AWS"],
            },
            {
                "title": "Frontend Developer (React / Next.js)",
                "company": "Apex Digital",
                "location": "New York, NY (On-site)",
                "job_type": "Full-time",
                "salary_min": 80000,
                "salary_max": 110000,
                "description": "Create responsive, accessible user interfaces using React, TypeScript, and modern CSS libraries. Work closely with product designers to implement interactive data dashboards.",
                "required_skills": ["React", "JavaScript", "TypeScript", "Git"],
                "preferred_skills": ["REST API", "GraphQL", "Problem Solving"],
            },
            {
                "title": "Cloud DevOps & Platform Engineer",
                "company": "Vanguard Cloud Services",
                "location": "Austin, TX (Hybrid)",
                "job_type": "Full-time",
                "salary_min": 95000,
                "salary_max": 130000,
                "description": "Automate cloud infrastructure deployments using Docker, Kubernetes, AWS, and CI/CD pipelines. Monitor infrastructure reliability and maintain container registries.",
                "required_skills": ["Docker", "Kubernetes", "AWS", "Linux", "CI/CD"],
                "preferred_skills": ["Python", "SQL", "Git"],
            },
            {
                "title": "Associate Data Engineer",
                "company": "InsightFlow Analytics",
                "location": "Remote",
                "job_type": "Full-time",
                "salary_min": 80000,
                "salary_max": 105000,
                "description": "Design and optimize relational data pipelines with PostgreSQL and SQL. Transform raw data feeds into structured analytical schemas for downstream machine learning models.",
                "required_skills": ["SQL", "PostgreSQL", "Python", "Git"],
                "preferred_skills": ["Docker", "AWS", "Machine Learning"],
            },
        ]

        created_jobs = 0
        for job_info in jobs_data:
            existing_job = db.query(Job).filter(Job.title == job_info["title"], Job.company == job_info["company"]).first()
            if not existing_job:
                # Get or create company
                comp = db.query(Company).filter(Company.name == job_info["company"]).first()
                if not comp:
                    comp = Company(name=job_info["company"], location=job_info["location"])
                    db.add(comp)
                    db.flush()

                job = Job(
                    source_id=source.id,
                    company_id=comp.id,
                    external_id=f"internal:{job_info['title']}:{job_info['company']}",
                    title=job_info["title"],
                    company=job_info["company"],
                    location=job_info["location"],
                    job_type=job_info["job_type"],
                    salary_min=job_info["salary_min"],
                    salary_max=job_info["salary_max"],
                    description=job_info["description"],
                    is_active=True,
                )
                db.add(job)
                db.flush()

                # Add job skills
                for skill_name in job_info["required_skills"]:
                    sk = skill_map.get(skill_name)
                    if sk:
                        db.add(JobSkill(job_id=job.id, skill_id=sk.id, skill_type="required", importance=1.0, required_proficiency=3))

                for skill_name in job_info["preferred_skills"]:
                    sk = skill_map.get(skill_name)
                    if sk:
                        db.add(JobSkill(job_id=job.id, skill_id=sk.id, skill_type="preferred", importance=0.8, required_proficiency=2))

                created_jobs += 1

        logger.info("Seeded %d real-world tech jobs with required and preferred skills.", created_jobs)

        # 5. Seed Courses
        courses_data = [
            ("Mastering FastAPI & Asynchronous Python", "Coursera", "https://coursera.org/learn/fastapi", "Python", 4.8),
            ("Production PostgreSQL & Database Design", "Udemy", "https://udemy.com/course/postgresql", "PostgreSQL", 4.9),
            ("Docker & Kubernetes for Modern Developers", "edX", "https://edx.org/course/docker-kubernetes", "Docker", 4.7),
            ("React 19 & Full-Stack TypeScript Mastery", "Pluralsight", "https://pluralsight.com/courses/react-typescript", "React", 4.8),
            ("Applied Machine Learning & Sentence Transformers", "DeepLearning.AI", "https://deeplearning.ai/courses/nlp-transformers", "Machine Learning", 4.9),
        ]

        for title, provider, url, skill_name, rating in courses_data:
            existing_course = db.query(Course).filter(Course.title == title).first()
            if not existing_course:
                db.add(Course(title=title, provider=provider, url=url, skill_name=skill_name, rating=rating))

        logger.info("Seeded %d online courses for roadmap recommendations.", len(courses_data))

        db.commit()
        logger.info("PostgreSQL database seeding finished successfully!")

    except Exception as exc:
        db.rollback()
        logger.error("Seeding failed: %s", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
