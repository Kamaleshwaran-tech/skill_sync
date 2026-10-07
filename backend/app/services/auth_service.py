from __future__ import annotations

from datetime import datetime, timezone
from typing import Tuple

from sqlalchemy.orm import Session

from app.repositories.auth_repository import get_user_by_email, create_user, get_user_by_id
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.utils.validation import is_valid_password
from app.models.auth_models import RefreshToken


def register_user(db: Session, email: str, password: str, full_name: str | None = None, role: str = "CANDIDATE"):
    existing = get_user_by_email(db, email)
    if existing:
        raise ValueError("Email already registered")
    if not is_valid_password(password):
        raise ValueError("Password must include upper-case, lower-case, and numeric characters.")
    hashed = hash_password(password)
    return create_user(db, email=email, hashed_password=hashed, full_name=full_name, role=role)


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not user.hashed_password or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_tokens(db: Session, user) -> Tuple[str, str]:
    access_token, access_jti = create_access_token(user.id)
    refresh_token, refresh_jti, expires_at = create_refresh_token(user.id)
    # store refresh token record
    rt = RefreshToken(user_id=user.id, jti=refresh_jti, revoked=False, expires_at=expires_at)
    db.add(rt)
    db.commit()
    return access_token, refresh_token


def revoke_refresh_token(db: Session, jti: str) -> None:
    token = db.query(RefreshToken).filter(RefreshToken.jti == jti).one_or_none()
    if token:
        token.revoked = True
        db.add(token)
        db.commit()


def is_refresh_token_valid(db: Session, jti: str) -> bool:
    token = db.query(RefreshToken).filter(RefreshToken.jti == jti).one_or_none()
    if not token:
        return False
    if token.revoked:
        return False

    expires_at = token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at = expires_at.astimezone(timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        return False
    return True
