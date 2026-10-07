from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO

from app.utils.storage import StorageBackend


class LocalStorage(StorageBackend):
    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _full_path(self, destination_path: str) -> Path:
        return self.base_path / destination_path

    def save(self, fileobj: BinaryIO, destination_path: str) -> None:
        full = self._full_path(destination_path)
        full.parent.mkdir(parents=True, exist_ok=True)
        # ensure binary mode
        with open(full, "wb") as f:
            # read in chunks
            for chunk in iter(lambda: fileobj.read(8192), b""):
                f.write(chunk)

    def delete(self, destination_path: str) -> None:
        full = self._full_path(destination_path)
        if full.exists():
            full.unlink()

    def url(self, destination_path: str) -> str:
        # For local dev, return path as file:// URI
        full = self._full_path(destination_path).resolve()
        return f"file://{full.as_posix()}"
