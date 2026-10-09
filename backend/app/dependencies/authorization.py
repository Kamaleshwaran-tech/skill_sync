from __future__ import annotations

from fastapi import HTTPException, status


def ensure_job_management_access(current_user, job) -> None:
    """Allow administrators or the employer assigned to the job's company."""
    if (current_user.role or "").upper() == "ADMIN":
        return

    employer_profile = getattr(current_user, "employer_profile", None)
    if (
        (current_user.role or "").upper() != "EMPLOYER"
        or employer_profile is None
        or employer_profile.company_id is None
        or employer_profile.company_id != job.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage this job.",
        )
