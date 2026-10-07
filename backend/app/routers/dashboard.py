from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db_session
from app.dependencies.auth import get_current_user
from app.schemas.dashboard import (
    DashboardAnalysisResponse,
    DashboardResponse,
    TargetRoleRequest,
    TargetRoleResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    service = DashboardService()
    return service.build_dashboard(db, current_user)


@router.get("/target-role", response_model=TargetRoleResponse)
def get_target_role(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    service = DashboardService()
    return service.get_target_role(db, current_user)


@router.post("/target-role", response_model=TargetRoleResponse)
def set_target_role(
    payload: TargetRoleRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    service = DashboardService()
    return service.set_target_role(db, current_user, payload.targetRole)


@router.post("/analyze", response_model=DashboardAnalysisResponse)
def analyze_for_target_role(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    service = DashboardService()
    try:
        return service.run_analysis(db, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
