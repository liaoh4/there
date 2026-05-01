# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Major Compass** — 高中生专业选择决策支持系统 (high-school student major-selection decision support system).

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript |
| Backend | FastAPI + Python 3.12 + SQLAlchemy 2.0 async |
| Task queue | Celery (Redis broker) |
| Primary DB | PostgreSQL 16 |
| Cache | Redis 7 |
| Graph DB | Neo4j — planned for v2, not active |

## Local Development

```bash
# Start infrastructure only
docker compose up -d postgres redis

# Backend
cd backend
pip install -e ".[dev]"
alembic upgrade head
python data/scripts/seed.py
uvicorn app.main:app --reload
# Swagger UI: http://localhost:8000/docs

# Frontend
cd frontend && npm install && npm run dev
# http://localhost:3000

# Full stack (includes Celery worker)
docker compose up
```

## Testing

```bash
cd backend && pytest -v

# Run a single test file
pytest tests/test_scoring.py -v
```

The scoring service (`app/services/scoring.py`) is pure functions with no DB dependency — its tests run instantly without any infrastructure.

## Backend Architecture

```
backend/
  app/
    api/v1/       REST layer — parameter validation and routing only
    services/     Business logic — pure functions, no FastAPI/SQLAlchemy imports
    models/       SQLAlchemy ORM models
    schemas/      Pydantic v2 request/response models
    workers/      Celery tasks (scrapers, NLP)
```

**The service layer must stay framework-free.** `app/services/scoring.py` imports nothing from FastAPI or SQLAlchemy. This is intentional so unit tests need no HTTP server or database.

## Assessment Flow

1. `POST /api/v1/sessions` — session created immediately (before first answer)
2. `POST /api/v1/sessions/{id}/responses` — idempotent batch upsert; frontend calls this incrementally
3. `POST /api/v1/sessions/{id}/complete` — computes RIASEC scores + runs `rank_majors()`, persists recommendations, marks session completed. Idempotent.
4. `GET /api/v1/sessions/{id}/result` — retrieves cached result

Scores and recommendations are written once on completion and never recomputed, so A/B testing new weights won't corrupt historical data.

## RIASEC Scoring

`compute_riasec(responses)` maps question IDs (`r1`, `r2`, `i1` …) to the six RIASEC dimensions, normalises raw Likert sums to 0–100, then `rank_majors()` ranks active majors by cosine similarity between the user's normalised vector and each major's stored profile.

Major RIASEC profiles are stored as six `DECIMAL(3,2)` columns (not JSON) to allow future pgvector cosine queries at the DB layer.

## Key Data Model Decisions

- **Soft delete** — `Major.is_active` flag; never hard-delete because `assessment_recommendations` holds foreign keys to `majors.id`.
- **`algorithm_version`** on `AssessmentSession` — allows re-running scoring after weight changes without touching historical rows.
- **`AssessmentResponse`** has a `(session_id, question_id)` unique constraint — supports safe re-submission.

## API Versioning

All routes are prefixed `/api/v1/`. Breaking changes get a new `/api/v2/`; `v1` is kept for at least one major release cycle. Non-breaking additive fields are added in-place (Pydantic ignores unknown fields by default).
