from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import get_settings
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import add_request_logging_middleware
from app.middleware.compression import WorkspaceCompression
from app.routers import auth, health, resumes, jobs
from app.utils.logging import configure_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(app):
    configure_logging()
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Login, parse a resume locally, and rank current Adzuna job search results against that exact resume.",
    lifespan=lifespan,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(WorkspaceCompression, api_prefix=settings.api_prefix)
register_exception_handlers(app)
add_request_logging_middleware(app)
app.include_router(auth.router, prefix=settings.api_prefix + "/auth")
for router in [health.router, resumes.router, jobs.router]:
    app.include_router(router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {"message": "SkillSync resume-to-Adzuna matching API"}
