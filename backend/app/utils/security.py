from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid
from typing import Tuple

from passlib.context import CryptContext
import jwt

from app.config.settings import get_settings
from app.models.auth_models import RevokedAccessToken

# use pbkdf2_sha256 to avoid system bcrypt binary/backend issues in test environments
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _jti() -> str:
    return str(uuid.uuid4())


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> Tuple[str, str]:
    jti = _jti()
    expire = _now() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {
        "sub": str(subject),
        "exp": int(expire.timestamp()),
        "jti": jti,
        "type": "access",
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti


def create_refresh_token(subject: str | int, expires_delta: timedelta | None = None) -> Tuple[str, str, datetime]:
    jti = _jti()
    expire = _now() + (expires_delta or timedelta(days=settings.refresh_token_expire_days))
    payload = {
        "sub": str(subject),
        "exp": int(expire.timestamp()),
        "jti": jti,
        "type": "refresh",
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti, expire


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def revoke_access_token(db, token: str) -> None:
    payload = decode_token(token)
    if payload.get("type") != "access":
        return
    jti = payload.get("jti")
    if not jti:
        return
    if db.query(RevokedAccessToken).filter(RevokedAccessToken.jti == jti).one_or_none():
        return
    db.add(
        RevokedAccessToken(
            user_id=int(payload["sub"]),
            jti=jti,
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
    )
    db.commit()


def is_access_token_revoked(db, jti: str | None) -> bool:
    if not jti:
        return True
    return db.query(RevokedAccessToken.id).filter(RevokedAccessToken.jti == jti).first() is not None
