from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserOut
from app.database.session import get_db_session
from app.services.auth_service import register_user, authenticate_user, create_tokens, revoke_refresh_token, is_refresh_token_valid
from app.repositories.auth_repository import get_user_by_id
from app.utils.security import decode_token, revoke_access_token
from app.dependencies.auth import get_current_user as get_current_user_dep

router = APIRouter(tags=["Auth"])
security = HTTPBearer()


@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest, db: Session = Depends(get_db_session)):
    # basic password strength enforcement already via pydantic min_length; additional checks can be added
    try:
        user = register_user(db, payload.email, payload.password, payload.full_name, payload.role or "CANDIDATE")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db_session)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token, refresh_token = create_tokens(db, user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db_session)):
    # decode refresh token and validate
    try:
        data = decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    jti = data.get("jti")
    if not is_refresh_token_valid(db, jti):
        raise HTTPException(status_code=401, detail="Refresh token invalid or revoked")
    # rotate: revoke old
    revoke_refresh_token(db, jti)
    # create tokens for user
    user_id = int(data.get("sub"))
    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive or no longer exists")
    access_token, refresh_token = create_tokens(db, user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
def logout(payload: RefreshRequest, request: Request, current_user=Depends(get_current_user_dep), db: Session = Depends(get_db_session)):
    try:
        data = decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    jti = data.get("jti")
    if data.get("sub") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Refresh token does not belong to the authenticated user")
    revoke_refresh_token(db, jti)
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        revoke_access_token(db, authorization.split(" ", 1)[1])
    return {"detail": "Logged out"}

@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user_dep)):
    return current_user
