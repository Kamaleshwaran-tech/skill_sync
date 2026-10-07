# SkillSync AI Backend

This directory contains the FastAPI foundation for the SkillSync AI backend.

## Scope

This is the foundational backend scaffold only. It includes:

- FastAPI application setup
- environment variable handling
- SQLAlchemy configuration
- Alembic configuration
- CORS and logging setup
- global exception handlers
- health endpoint
- dependency injection structure
- testing setup

Business features such as resume processing, AI analysis, jobs, and auth are deliberately not implemented in this phase.

## Local development

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Production hardening overview

This backend is configured for production-oriented deployment with:

- environment-based configuration
- rate limiting
- structured JSON logging
- security headers
- CORS restrictions via env configuration
- DB health checks
- file upload validation
- JWT secret enforcement in production

## Health checks

```bash
curl http://localhost:8000/api/v1/health
```

## Migration commands

```bash
cd backend
python -m alembic upgrade head
```

To generate a new migration:

```bash
cd backend
python -m alembic revision --autogenerate -m "describe change"
```

## Docker deployment

From the repository root:

```bash
docker compose up --build
```

Then verify:

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/docs
```

## Security notes

- Never commit real `.env` files or JWT secrets.
- Rotate secrets regularly and inject them via CI/CD or a secret manager.
- Keep file uploads limited and validated before writing to disk.
- Restrict CORS origins to trusted frontend domains in production.
