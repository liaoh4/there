from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config import get_settings
from app.exceptions import (
    InsufficientResponsesError,
    MajorCompassError,
    SessionAbandonedError,
    SessionNotFoundError,
)
from app.middleware.logging import RequestLoggingMiddleware

app = FastAPI(
    title="Major Compass API",
    description="高中生专业选择决策支持系统",
    version="1.0.0",
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────

@app.exception_handler(SessionNotFoundError)
async def session_not_found_handler(request: Request, exc: SessionNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(SessionAbandonedError)
async def session_abandoned_handler(request: Request, exc: SessionAbandonedError) -> JSONResponse:
    return JSONResponse(status_code=410, content={"detail": str(exc)})


@app.exception_handler(InsufficientResponsesError)
async def insufficient_responses_handler(
    request: Request, exc: InsufficientResponsesError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": str(exc),
            "answered": exc.answered,
            "required": exc.required,
        },
    )


@app.exception_handler(MajorCompassError)
async def generic_domain_error_handler(request: Request, exc: MajorCompassError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# ── Routes ────────────────────────────────────────────────────────────────────

app.include_router(api_router)


@app.get("/health", tags=["ops"])
async def health_check() -> dict:
    return {"status": "ok"}
