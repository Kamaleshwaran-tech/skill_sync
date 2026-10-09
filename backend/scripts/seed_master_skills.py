from __future__ import annotations

import sys
from pathlib import Path

# Ensure package imports work when run as a script
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database.session import SessionLocal
from app.models.models import Skill

MASTER_SKILLS = [
    "Python",
    "JavaScript",
    "TypeScript",
    "React",
    "Node.js",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "Git",
    "Linux",
]


def seed_skills() -> None:
    db = SessionLocal()
    try:
        for name in MASTER_SKILLS:
            existing = db.query(Skill).filter(Skill.name == name).first()
            if not existing:
                db.add(Skill(name=name))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_skills()
    print("Seeded master skills (if they did not already exist).")
