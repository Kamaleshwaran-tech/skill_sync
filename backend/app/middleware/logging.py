from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict, deque

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config.settings import get_settings

logger = logging.getLogger("skillsync_ai")
settings = get_settings()

rate_limit_store: dict[str, deque[float]] = defaultdict(deque)


async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(
        "request_processed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    response.headers["x-request-id"] = request_id
    response.headers["x-frame-options"] = "DENY"
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["referrer-policy"] = "strict-origin-when-cross-origin"
    response.headers["permissions-policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.scheme == "https" or settings.environment.lower() == "production":
        response.headers["strict-transport-security"] = "max-age=31536000; includeSubDomains"
    return response


async def rate_limit_and_security(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = rate_limit_store[client_ip]
    while window and now - window[0] > 60:
        window.popleft()

    if len(window) >= settings.rate_limit_per_minute:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."},
        )

    window.append(now)
    return await log_requests(request, call_next)


def add_request_logging_middleware(app: FastAPI) -> None:
    app.middleware("http")(rate_limit_and_security)
