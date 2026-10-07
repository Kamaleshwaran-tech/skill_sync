from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class JobProvider(ABC):
    name: str = "provider"

    @abstractmethod
    def fetch_jobs(
        self,
        query: str | None = None,
        location: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError

    @property
    def is_configured(self) -> bool:
        return True
