from __future__ import annotations

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_db_session
from app.utils.security import decode_token, is_access_token_revoked
from app.repositories.auth_repository import get_user_by_id

security = HTTPBearer(auto_error=False)


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)], db: Session = Depends(get_db_session)):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication credentials are required")
    token = credentials.credentials
    try:
        data = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    if data.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    if is_access_token_revoked(db, data.get("jti")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    user_id = int(data.get("sub"))
    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_roles(*roles: str) -> Callable:
    allowed_roles = {role.upper() for role in roles}

    def dependency(current_user=Depends(get_current_user)):
        if (current_user.role or "").upper() not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")
        return current_user

    return dependency


def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Session = Depends(get_db_session),
):
    if credentials is None:
        return None
    try:
        data = decode_token(credentials.credentials)
        if data.get("type") != "access" or is_access_token_revoked(db, data.get("jti")):
            return None
        user_id = int(data.get("sub"))
        user = get_user_by_id(db, user_id)
        if not user or not user.is_active:
            return None
        return user
    except Exception:
        return None

