from __future__ import annotations

from typing import List
from app.ai.interfaces.recommendation_engine import (
    RecommendationEngineInterface,
    RecommendationPayload,
    RecommendedCertification,
    RecommendedProject,
    RecommendedResource,
)

RESOURCE_CATALOG = {
    "python": [
        RecommendedResource(title="Python Official Documentation", type="documentation", url="https://docs.python.org/3/", source="Python.org"),
        RecommendedResource(title="Python for Everybody", type="course", url="https://www.coursera.org/specializations/python", source="Coursera"),
    ],
    "react": [
        RecommendedResource(title="React Interactive Documentation", type="documentation", url="https://react.dev/", source="React"),
        RecommendedResource(title="Complete React Developer", type="course", url="https://frontendmasters.com", source="Frontend Masters"),
    ],
    "postgresql": [
        RecommendedResource(title="PostgreSQL Official Manual", type="documentation", url="https://www.postgresql.org/docs/", source="PostgreSQL"),
    ],
    "docker": [
        RecommendedResource(title="Docker Deep Dive", type="documentation", url="https://docs.docker.com/get-started/", source="Docker"),
    ],
    "aws": [
        RecommendedResource(title="AWS Cloud Practitioner Essentials", type="course", url="https://aws.amazon.com/training/", source="AWS"),
    ],
}

CERT_MAP = {
    "python": RecommendedCertification(title="PCPP - Certified Professional in Python Programming", skill="Python", issuer="Python Institute"),
    "react": RecommendedCertification(title="Meta Front-End Developer Professional Certificate", skill="React", issuer="Meta"),
    "postgresql": RecommendedCertification(title="PostgreSQL Certified Associate", skill="PostgreSQL", issuer="PostgreSQL Org"),
    "docker": RecommendedCertification(title="Docker Certified Associate (DCA)", skill="Docker", issuer="Mirantis / Docker"),
    "aws": RecommendedCertification(title="AWS Certified Cloud Practitioner", skill="AWS", issuer="Amazon Web Services"),
}


class RuleRecommendationEngine(RecommendationEngineInterface):
    """Generates targeted project, certification, and resource recommendations."""

    def generate_recommendations(
        self,
        target_role: str,
        missing_skills: List[str],
        current_skills: List[str],
    ) -> RecommendationPayload:
        projects: List[RecommendedProject] = []
        certs: List[RecommendedCertification] = []
        resources: List[RecommendedResource] = []

        top_missing = [s.strip().lower() for s in missing_skills[:4]]

        for skill in top_missing:
            # Add project recommendation
            projects.append(
                RecommendedProject(
                    title=f"Build a {skill.title()} Production Application",
                    goal=f"Develop a complete project using {skill.title()} tailored for {target_role} requirements.",
                    missing_skills=[skill.title()],
                    difficulty="Intermediate",
                )
            )

            # Add certification recommendation if available
            if skill in CERT_MAP:
                certs.append(CERT_MAP[skill])

            # Add resources if available
            if skill in RESOURCE_CATALOG:
                resources.extend(RESOURCE_CATALOG[skill])
            else:
                resources.append(
                    RecommendedResource(
                        title=f"Official {skill.title()} Learning Guide",
                        type="documentation",
                        url=f"https://google.com/search?q={skill}+official+docs",
                        source="Web Documentation",
                    )
                )

        if not projects:
            projects.append(
                RecommendedProject(
                    title=f"{target_role} Portfolio Polish",
                    goal="Refactor existing repos, add CI/CD pipelines, and write comprehensive architecture documentation.",
                    missing_skills=[],
                    difficulty="Advanced",
                )
            )

        return RecommendationPayload(
            projects=projects,
            certifications=certs,
            resources=resources,
        )
