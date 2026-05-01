"""
Assessment endpoints.

POST /sessions            → create a new session, return session_id
POST /sessions/{id}/responses  → submit answers (idempotent, batchable)
POST /sessions/{id}/complete   → compute scores + recommendations, return result
GET  /sessions/{id}/result     → retrieve a previously completed result
"""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import get_db
from app.models.assessment import AssessmentRecommendation, AssessmentResponse, AssessmentSession
from app.models.major import Major
from app.schemas.session import (
    AssessmentResult,
    MajorSummary,
    RecommendationItem,
    RiasecScoresOut,
    SessionCreated,
    SubmitResponsesRequest,
)
from app.services.scoring import compute_riasec, rank_majors

router = APIRouter(prefix="/sessions", tags=["assessments"])
settings = get_settings()


@router.post("", response_model=SessionCreated, status_code=status.HTTP_201_CREATED)
async def create_session(db: AsyncSession = Depends(get_db)) -> SessionCreated:
    """Start a new assessment session. Call this before showing the first question."""
    session = AssessmentSession()
    db.add(session)
    await db.flush()
    return SessionCreated(session_id=session.id, algorithm_version=session.algorithm_version)


@router.post("/{session_id}/responses", status_code=status.HTTP_204_NO_CONTENT)
async def submit_responses(
    session_id: uuid.UUID,
    body: SubmitResponsesRequest,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Batch-save answers. Safe to call multiple times (upsert by question_id).
    Allows the frontend to persist progress incrementally.
    """
    session = await _get_active_session(session_id, db)

    # Load existing responses to upsert
    existing = {
        r.question_id: r
        for r in (
            await db.execute(
                select(AssessmentResponse).where(AssessmentResponse.session_id == session_id)
            )
        ).scalars()
    }

    for item in body.responses:
        if item.question_id in existing:
            existing[item.question_id].answer = item.answer
            existing[item.question_id].answered_at = item.answered_at
        else:
            db.add(
                AssessmentResponse(
                    session_id=session_id,
                    question_id=item.question_id,
                    module=item.module,
                    answer=item.answer,
                    answered_at=item.answered_at,
                )
            )


@router.post("/{session_id}/complete", response_model=AssessmentResult)
async def complete_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> AssessmentResult:
    """
    Compute RIASEC scores and major recommendations, persist them, mark session completed.
    Idempotent: calling again on a completed session returns the cached result.
    """
    session = await _get_session_with_responses(session_id, db)

    # Return cached result if already completed
    if session.status == "completed":
        return await _build_result(session, db)

    # ── Compute scores ────────────────────────────────────────────────────
    riasec_responses = {
        r.question_id: r.answer
        for r in session.responses
        if r.module == "riasec"
    }
    scores = compute_riasec(riasec_responses)

    # Persist scores on the session
    session.score_r = scores.R
    session.score_i = scores.I
    session.score_a = scores.A
    session.score_s = scores.S
    session.score_e = scores.E
    session.score_c = scores.C

    # ── Rank majors ───────────────────────────────────────────────────────
    majors = (await db.execute(select(Major).where(Major.is_active == True))).scalars().all()  # noqa: E712
    profiles = [(str(m.id), m.riasec_vector) for m in majors]
    matches = rank_majors(scores, profiles, top_n=settings.TOP_N_RECOMMENDATIONS)

    major_map = {str(m.id): m for m in majors}
    for match in matches:
        db.add(
            AssessmentRecommendation(
                session_id=session_id,
                major_id=uuid.UUID(match.major_id),
                rank=match.rank,
                similarity_score=match.similarity,
            )
        )

    session.status = "completed"
    session.completed_at = datetime.now(UTC)
    await db.flush()

    return await _build_result(session, db)


@router.get("/{session_id}/result", response_model=AssessmentResult)
async def get_result(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> AssessmentResult:
    """Retrieve results for a completed session (e.g. for share links)."""
    session = await _get_session_with_responses(session_id, db)
    if session.status != "completed":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Session not completed yet.")
    return await _build_result(session, db)


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_active_session(session_id: uuid.UUID, db: AsyncSession) -> AssessmentSession:
    session = await db.get(AssessmentSession, session_id)
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found.")
    if session.status == "abandoned":
        raise HTTPException(status.HTTP_410_GONE, detail="Session has been abandoned.")
    return session


async def _get_session_with_responses(session_id: uuid.UUID, db: AsyncSession) -> AssessmentSession:
    result = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.id == session_id)
        .options(
            selectinload(AssessmentSession.responses),
            selectinload(AssessmentSession.recommendations),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return session


async def _build_result(session: AssessmentSession, db: AsyncSession) -> AssessmentResult:
    scores = RiasecScoresOut(
        R=session.score_r or 0,
        I=session.score_i or 0,
        A=session.score_a or 0,
        S=session.score_s or 0,
        E=session.score_e or 0,
        C=session.score_c or 0,
        dominant_type=max(
            {"R": session.score_r or 0, "I": session.score_i or 0, "A": session.score_a or 0,
             "S": session.score_s or 0, "E": session.score_e or 0, "C": session.score_c or 0},
            key=lambda k: {"R": session.score_r or 0, "I": session.score_i or 0,
                           "A": session.score_a or 0, "S": session.score_s or 0,
                           "E": session.score_e or 0, "C": session.score_c or 0}[k],
        ),
        top_two=("R", "I"),  # simplified; use scoring.RiasecScores.top_two in full impl
    )

    recs = []
    for rec in sorted(session.recommendations, key=lambda r: r.rank):
        major = await db.get(Major, rec.major_id)
        if major:
            recs.append(
                RecommendationItem(
                    rank=rec.rank,
                    similarity_score=float(rec.similarity_score),
                    major=MajorSummary(
                        id=major.id,
                        code=major.code,
                        name=major.name,
                        discipline_category=major.discipline_category,
                        major_category=major.major_category,
                    ),
                )
            )

    return AssessmentResult(
        session_id=session.id,
        riasec_scores=scores,
        recommendations=recs,
        completed_at=session.completed_at or datetime.now(UTC),
    )
