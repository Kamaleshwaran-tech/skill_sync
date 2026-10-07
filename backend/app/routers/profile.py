from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.database.session import get_db_session
from app.dependencies.auth import get_current_user
from app.models.models import CandidateProfile, Education, Experience, Skill, User, UserPreference, UserSkill


router = APIRouter(prefix="/profile", tags=["Profile"])


class EducationInput(BaseModel):
    school: str = Field(min_length=1, max_length=255)
    degree: str | None = Field(default=None, max_length=255)
    field: str | None = Field(default=None, max_length=255)
    graduationYear: str | None = Field(default=None, max_length=16)


class ExperienceInput(BaseModel):
    company: str = Field(min_length=1, max_length=255)
    role: str = Field(min_length=1, max_length=255)
    period: str | None = Field(default=None, max_length=64)
    summary: str | None = Field(default=None, max_length=5000)


class ProfileUpdate(BaseModel):
    firstName: str | None = Field(default=None, max_length=120)
    lastName: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=64)
    location: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=5000)
    website: str | None = Field(default=None, max_length=1024)
    linkedIn: str | None = Field(default=None, max_length=1024)
    education: list[EducationInput] | None = None
    experience: list[ExperienceInput] | None = None
    skills: list[str] | None = None
    careerPreferences: dict[str, Any] | None = None
    targetRoles: list[str] | None = None


class SettingsUpdate(BaseModel):
    theme: str | None = Field(default=None, max_length=32)
    notifications: dict[str, bool] | None = None
    privacy: dict[str, bool] | None = None
    account: dict[str, Any] | None = None


def _get_or_create_preferences(db: Session, user_id: int) -> UserPreference:
    preferences = db.query(UserPreference).filter(UserPreference.user_id == user_id).one_or_none()
    if preferences is None:
        preferences = UserPreference(user_id=user_id, preferences={})
        db.add(preferences)
        db.flush()
    return preferences


def _serialize_profile(db: Session, user: User) -> dict[str, Any]:
    candidate = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).one_or_none()
    preferences = _get_or_create_preferences(db, user.id).preferences or {}
    first_name, _, last_name = (user.full_name or "").partition(" ")
    return {
        "firstName": first_name,
        "lastName": last_name,
        "email": user.email,
        "phone": candidate.phone if candidate else "",
        "location": candidate.location if candidate else "",
        "bio": candidate.bio if candidate else "",
        "website": preferences.get("website", ""),
        "linkedIn": candidate.linkedin_url if candidate else "",
        "education": [
            {
                "school": item.institution,
                "degree": item.degree or "",
                "field": item.field_of_study or "",
                "graduationYear": item.grade or "",
            }
            for item in db.query(Education).filter(Education.user_id == user.id).all()
        ],
        "experience": [
            {
                "company": item.company,
                "role": item.title,
                "period": item.location or "",
                "summary": item.description or "",
            }
            for item in db.query(Experience).filter(Experience.user_id == user.id).all()
        ],
        "skills": [item.skill.name for item in user.skills if item.skill],
        "careerPreferences": preferences.get("careerPreferences", {}),
        "targetRoles": preferences.get("targetRoles", []),
    }


@router.get("")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    profile = _serialize_profile(db, current_user)
    db.commit()
    return profile


@router.put("")
def update_profile(payload: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    candidate = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).one_or_none()
    if candidate is None:
        candidate = CandidateProfile(user_id=current_user.id)
        db.add(candidate)

    if payload.firstName is not None or payload.lastName is not None:
        current_user.full_name = " ".join(part for part in [payload.firstName or "", payload.lastName or ""] if part).strip() or current_user.full_name
    for field in ("phone", "location", "bio"):
        value = getattr(payload, field)
        if value is not None:
            setattr(candidate, field, value.strip() or None)
    if payload.linkedIn is not None:
        candidate.linkedin_url = payload.linkedIn.strip() or None

    preferences = _get_or_create_preferences(db, current_user.id)
    preference_values = dict(preferences.preferences or {})
    if payload.website is not None:
        preference_values["website"] = payload.website.strip()
    if payload.careerPreferences is not None:
        preference_values["careerPreferences"] = payload.careerPreferences
    if payload.targetRoles is not None:
        preference_values["targetRoles"] = payload.targetRoles
    preferences.preferences = preference_values

    if payload.education is not None:
        db.query(Education).filter(Education.user_id == current_user.id).delete()
        for item in payload.education:
            db.add(Education(
                user_id=current_user.id,
                institution=item.school,
                degree=item.degree,
                field_of_study=item.field,
                grade=item.graduationYear,
            ))
    if payload.experience is not None:
        db.query(Experience).filter(Experience.user_id == current_user.id).delete()
        for item in payload.experience:
            db.add(Experience(
                user_id=current_user.id,
                company=item.company,
                title=item.role,
                location=item.period,
                description=item.summary,
            ))
    if payload.skills is not None:
        requested = {skill.strip() for skill in payload.skills if skill.strip()}
        existing_profile_skills = db.query(UserSkill).filter(
            UserSkill.user_id == current_user.id,
            UserSkill.source == "profile",
        ).all()
        for association in existing_profile_skills:
            if association.skill and association.skill.name not in requested:
                db.delete(association)
        existing_names = {association.skill.name for association in current_user.skills if association.skill}
        for name in requested - existing_names:
            skill = db.query(Skill).filter(Skill.name == name).one_or_none()
            if skill is None:
                skill = Skill(name=name, category="technical")
                db.add(skill)
                db.flush()
            db.add(UserSkill(user_id=current_user.id, skill_id=skill.id, source="profile"))

    db.commit()
    db.refresh(current_user)
    return _serialize_profile(db, current_user)


@router.get("/settings")
def get_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    preferences = _get_or_create_preferences(db, current_user.id)
    db.commit()
    return preferences.preferences.get("settings", {})


@router.put("/settings")
def update_settings(payload: SettingsUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    preferences = _get_or_create_preferences(db, current_user.id)
    values = dict(preferences.preferences or {})
    values["settings"] = payload.model_dump(exclude_none=True)
    preferences.preferences = values
    db.commit()
    return values["settings"]
