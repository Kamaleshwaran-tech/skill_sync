from __future__ import annotations

from app.config.settings import Settings, get_settings


def get_settings_dependency() -> Settings:
    return get_settings()
