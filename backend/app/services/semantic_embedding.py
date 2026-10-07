from __future__ import annotations

from functools import lru_cache
from math import sqrt

import httpx

from app.config.settings import get_settings


class GeminiEmbeddingService:
    """Optional semantic similarity backed by Gemini embeddings.

    Matching must remain available when the provider is unavailable, so callers
    receive ``None`` on provider errors and use their deterministic fallback.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return bool(self.settings.semantic_embedding_enabled and self.settings.gemini_api_key)

    def similarity(self, left: str, right: str) -> float | None:
        if not self.enabled or not left.strip() or not right.strip():
            return None
        left_embedding = self._embed(left[:12000])
        right_embedding = self._embed(right[:12000])
        if not left_embedding or not right_embedding:
            return None
        dot = sum(a * b for a, b in zip(left_embedding, right_embedding))
        magnitude = sqrt(sum(a * a for a in left_embedding)) * sqrt(sum(b * b for b in right_embedding))
        return max(0.0, min(1.0, dot / magnitude)) if magnitude else None

    @lru_cache(maxsize=1024)
    def _embed(self, text: str) -> tuple[float, ...] | None:
        url = (
            f"{self.settings.gemini_base_url.rstrip('/')}/models/"
            f"{self.settings.gemini_embedding_model}:embedContent?key={self.settings.gemini_api_key}"
        )
        try:
            with httpx.Client(timeout=min(self.settings.gemini_timeout_seconds, 8.0)) as client:
                response = client.post(url, json={"content": {"parts": [{"text": text}]}})
                response.raise_for_status()
            values = response.json().get("embedding", {}).get("values", [])
            return tuple(float(value) for value in values) if values else None
        except (httpx.HTTPError, ValueError, TypeError):
            return None
