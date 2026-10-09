from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageBackend(ABC):
    @abstractmethod
    def save(self, fileobj: BinaryIO, destination_path: str) -> None:
        ...

    @abstractmethod
    def delete(self, destination_path: str) -> None:
        ...

    @abstractmethod
    def url(self, destination_path: str) -> str:
        ...
