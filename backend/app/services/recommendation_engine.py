from __future__ import annotations

from typing import Any


class RecommendationEngineService:
    """Deterministic recommendation generation without LLM hallucination."""

    TRUSTED_LEARNING_RESOURCES = {
        "python": [
            {"title": "Python Official Tutorial", "type": "documentation", "url": "https://docs.python.org/3/tutorial/", "source": "Python.org"},
            {"title": "Python for Everybody", "type": "course", "url": None, "source": "Coursera"},
        ],
        "docker": [
            {"title": "Docker Documentation", "type": "documentation", "url": "https://docs.docker.com/", "source": "Docker"},
        ],
        "postgresql": [
            {"title": "PostgreSQL Documentation", "type": "documentation", "url": "https://www.postgresql.org/docs/", "source": "PostgreSQL"},
        ],
        "react": [
            {"title": "React Docs", "type": "documentation", "url": "https://react.dev/learn", "source": "React"},
        ],
        "node.js": [
            {"title": "Node.js Docs", "type": "documentation", "url": "https://nodejs.org/en/docs/", "source": "Node.js"},
        ],
        "aws": [
            {"title": "AWS Skill Builder", "type": "course", "url": "https://skillbuilder.aws/", "source": "AWS"},
        ],
        "javascript": [
            {"title": "MDN JavaScript Guide", "type": "documentation", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "source": "MDN"},
        ],
    }

    CERTIFICATION_MAP = {
        "python": "Python Certification",
        "docker": "Docker Certified Associate",
        "aws": "AWS Certified Cloud Practitioner",
        "postgresql": "PostgreSQL Certification",
        "react": "React Developer Certification",
        "node.js": "Node.js Certified Developer",
        "javascript": "JavaScript Developer Certification",
    }

    PROJECT_TEMPLATES = {
        "postgresql": "Build a production-style full-stack application backed by PostgreSQL with CRUD flows, migrations, and analytics dashboards.",
        "docker": "Containerize a production-style application with Docker Compose and deployment scripts for a realistic multi-service setup.",
        "react": "Build a polished React UI with reusable components, state management, and a production-ready component library.",
        "node.js": "Create a Node.js backend with authentication, validation, and structured service layers.",
        "aws": "Deploy a small application stack on AWS and document architecture, costs, and environment configuration.",
        "javascript": "Build a JavaScript-heavy frontend or API project that demonstrates DOM patterns, async flows, and clean state logic.",
    }

    def generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        student_skills = {self._normalize_name(skill) for skill in payload.get("studentSkills", []) + payload.get("currentSkills", []) if str(skill).strip()}
        missing_skills = [self._normalize_name(skill) for skill in payload.get("missingSkills", []) if str(skill).strip()]
        target_role = str(payload.get("targetRole") or "Software Engineer")
        preferred_location = payload.get("preferredLocation")
        remote_preference = payload.get("remotePreference")
        experience_years = float(payload.get("experienceYears") or 0.0)
        priorities = payload.get("skillPriorities", {}) or {}
        industry_demand = payload.get("industryDemand", {}) or {}

        jobs = self._build_job_recommendations(payload.get("jobs", []), target_role, preferred_location, remote_preference, experience_years)
        skills = self._build_skill_recommendations(missing_skills, priorities, industry_demand)
        projects = self._build_project_recommendations(missing_skills)
        certifications = self._build_certifications(missing_skills)
        learning_resources = self._build_learning_resources(missing_skills)

        return {
            "jobs": jobs,
            "skills": skills,
            "projects": projects,
            "certifications": certifications,
            "learningResources": learning_resources,
        }

    def _build_job_recommendations(self, jobs: list[dict[str, Any]], target_role: str, preferred_location: str | None, remote_preference: str | None, experience_years: float) -> list[dict[str, Any]]:
        normalized_jobs = []
        for job in jobs:
            title = str(job.get("title") or job.get("name") or "Target Role")
            match_score = float(job.get("overall_match_score") or job.get("matchScore") or 0.0)
            location = str(job.get("location") or "Remote")
            required_skills = [self._display_name(skill) for skill in (job.get("required_skills") or job.get("requiredSkills") or [])]
            skill_coverage = float(job.get("required_skill_coverage") or job.get("skillCoverage") or 0.0)
            remote_fit = self._remote_fit(location, remote_preference)
            location_fit = self._location_fit(location, preferred_location)
            reason = (
                f"Strong alignment for {target_role} with a {match_score:.0f}% compatibility score and {skill_coverage:.0f}% required skill coverage."
            )
            normalized_jobs.append({
                "title": title,
                "company": str(job.get("company") or "Unlisted Company"),
                "location": location,
                "remotePreference": remote_fit,
                "matchScore": self._clamp(match_score, 0.0, 100.0),
                "reason": reason,
                "requiredSkills": required_skills,
                "skillCoverage": self._clamp(skill_coverage, 0.0, 100.0),
                "locationFit": location_fit,
            })

        sorted_jobs = sorted(normalized_jobs, key=lambda item: (item["matchScore"], item["skillCoverage"]), reverse=True)
        return sorted_jobs[:5]

    def _build_skill_recommendations(self, missing_skills: list[str], priorities: dict[str, str], industry_demand: dict[str, float]) -> list[dict[str, Any]]:
        recommendations = []
        for skill in missing_skills:
            normalized = self._normalize_name(skill)
            priority = str(priorities.get(skill, priorities.get(normalized, "MEDIUM"))).upper()
            demand = float(industry_demand.get(skill, industry_demand.get(normalized, 0.5)) or 0.5)
            prereqs = self._relevant_prerequisites(normalized)
            recommendations.append({
                "skill": self._display_name(normalized),
                "priority": priority,
                "reason": f"This skill addresses a high-impact gap for the target role and has strong market demand ({demand:.0%}).",
                "industryDemand": self._clamp(demand, 0.0, 1.0),
                "prerequisites": prereqs,
            })
        return sorted(recommendations, key=lambda item: self._priority_score(item["priority"]) + item["industryDemand"], reverse=True)

    def _build_project_recommendations(self, missing_skills: list[str]) -> list[dict[str, Any]]:
        if not missing_skills:
            return [{
                "title": "Portfolio polish sprint",
                "goal": "Strengthen the existing portfolio with a polished case study and refactor toward a production-ready deployment workflow.",
                "missingSkills": [],
                "difficulty": "Intermediate",
            }]

        projects = []
        for skill_name in missing_skills[:3]:
            normalized = self._normalize_name(skill_name)
            template = self.PROJECT_TEMPLATES.get(normalized, "Build a project that demonstrates practical implementation, testing, and deployment for the target role.")
            projects.append({
                "title": f"{self._display_name(normalized)} project challenge",
                "goal": template,
                "missingSkills": [self._display_name(normalized)],
                "difficulty": "Intermediate" if normalized in {"docker", "aws"} else "Beginner",
            })
        return projects

    def _build_certifications(self, missing_skills: list[str]) -> list[dict[str, Any]]:
        certs = []
        for skill_name in missing_skills[:3]:
            normalized = self._normalize_name(skill_name)
            title = self.CERTIFICATION_MAP.get(normalized)
            if not title:
                continue
            certs.append({
                "title": title,
                "provider": self._certification_provider(normalized),
                "focus": f"Validation of practical competence in {self._display_name(normalized)}.",
                "url": None,
            })
        return certs

    def _build_learning_resources(self, missing_skills: list[str]) -> list[dict[str, Any]]:
        resources = []
        seen = set()
        for skill_name in missing_skills[:4]:
            normalized = self._normalize_name(skill_name)
            for item in self.TRUSTED_LEARNING_RESOURCES.get(normalized, []):
                key = (item["title"], item["type"])
                if key in seen:
                    continue
                seen.add(key)
                resources.append({
                    "title": item["title"],
                    "type": item["type"],
                    "url": item.get("url"),
                    "source": item.get("source"),
                })
        if not resources:
            resources.append({
                "title": "General role-focused learning plan",
                "type": "course",
                "url": None,
                "source": "Internal guidance",
            })
        return resources

    def _relevant_prerequisites(self, skill: str) -> list[str]:
        prerequisites = {
            "docker": ["Linux"],
            "postgresql": ["SQL"],
            "node.js": ["JavaScript"],
            "react": ["JavaScript"],
            "aws": ["Cloud fundamentals"],
            "javascript": ["Programming fundamentals"],
            "python": ["Programming fundamentals"],
        }
        return prerequisites.get(skill, [])

    def _remote_fit(self, location: str, remote_preference: str | None) -> str:
        if not remote_preference:
            return "Flexible"
        normalized = str(remote_preference).lower()
        if normalized in {"remote", "hybrid", "onsite"}:
            return remote_preference.title()
        return "Flexible"

    def _location_fit(self, location: str, preferred_location: str | None) -> str:
        if preferred_location is None:
            return "Open to area fit"
        return "Matches preferred region" if str(preferred_location).lower() in str(location).lower() else "Consider relocation or remote option"

    def _priority_score(self, priority: str) -> float:
        return {"HIGH": 3.0, "MEDIUM": 2.0, "LOW": 1.0}.get(str(priority).upper(), 2.0)

    def _normalize_name(self, value: str) -> str:
        cleaned = str(value).strip().lower().replace("_", " ")
        cleaned = cleaned.replace("react.js", "react")
        cleaned = cleaned.replace("nodejs", "node.js")
        cleaned = cleaned.replace("postgres", "postgresql")
        return cleaned

    def _display_name(self, value: str) -> str:
        normalized = self._normalize_name(value)
        mapping = {
            "node.js": "Node.js",
            "postgresql": "PostgreSQL",
            "aws": "AWS",
            "javascript": "JavaScript",
            "react": "React",
            "docker": "Docker",
            "python": "Python",
        }
        return mapping.get(normalized, value.title())

    def _certification_provider(self, skill: str) -> str | None:
        mapping = {
            "python": "Python Software Foundation",
            "docker": "Docker",
            "aws": "AWS",
            "postgresql": "PostgreSQL Global Development Group",
            "react": "Meta",
            "node.js": "OpenJS Foundation",
            "javascript": "OpenJS Foundation",
        }
        return mapping.get(skill)

    def _clamp(self, value: float, lower: float, upper: float) -> float:
        return max(lower, min(upper, float(value)))
