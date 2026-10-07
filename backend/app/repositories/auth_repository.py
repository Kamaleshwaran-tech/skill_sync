from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).one_or_none()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).one_or_none()


def create_user(db: Session, email: str, hashed_password: str, full_name: str | None = None, role: str = "CANDIDATE") -> User:
    user = User(email=email, hashed_password=hashed_password, full_name=full_name, role=role.upper() if role else "CANDIDATE")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
