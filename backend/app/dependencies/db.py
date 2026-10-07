from __future__ import annotations

from typing import Any

from app.database.session import check_database_connection


def get_database_status() -> dict[str, Any]:
    healthy, message = check_database_connection()
    return {"healthy": healthy, "message": message}
