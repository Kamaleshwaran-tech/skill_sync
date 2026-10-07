"""
Input validation utilities.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email)) and len(email) <= 255


def is_valid_password(password: str) -> bool:
    """Validate password strength (minimum 8 chars, 1 upper, 1 lower, 1 digit)."""
    if len(password) < 8 or len(password) > 128:
        return False
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    return has_upper and has_lower and has_digit


def is_valid_url(url: str, allowed_schemes: tuple = ("http", "https")) -> bool:
    """Validate URL format and scheme."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in allowed_schemes and bool(parsed.netloc)
    except Exception:
        return False


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Remove leading/trailing whitespace and limit length."""
    return text.strip()[:max_length] if isinstance(text, str) else ""
