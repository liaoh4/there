"""
Assessment endpoints.

POST /sessions                    → create a new session, return session_id
POST /sessions/{id}/responses     → submit answers (idempotent, batchable)
POST /sessions/{id}/complete      → compute scores + recommendations, return result
GET  /sessions/{id}/result        → retrieve a previously completed result
"""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.exceptions import InsufficientResponsesError, SessionAbandonedError, SessionNotFoundError
from app.models.assessment import AssessmentSession
from app.models.major import Major
from app.repositories import assessment_repo, major_repo
from app.schemas.session import (
    AssessmentResult,
    MajorSummary,
    RecommendationItem,
    RiasecScoresOut,
    SessionCreated,
    SubmitResponsesRequest,
)
from app.services.scoring import RIASEC_QUESTION_MAP, RiasecScores, compute_riasec, rank_majors

router = APIRouter(prefix="/sessions", tags=["assessments"])
settings = get_settings()


@router.post("", response_model=SessionCreated, status_code=status.HTTP_201_CREATED)
async def create_session(db: AsyncSession = Depends(get_db)) -> SessionCreated:
    """Start a new assessment session. Call this before showing the first question."""
    session = await assessment_repo.create_session(db)
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
    session = await assessment_repo.get_session(db, session_id)
    if not session:
        raise SessionNotFoundError(session_id)
    if session.status == "abandoned":
        raise SessionAbandonedError(session_id)

    await assessment_repo.upsert_responses(db, session_id, body.responses)


@router.post("/{session_id}/complete", response_model=AssessmentResult)
async def complete_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> AssessmentResult:
    """
    Compute RIASEC scores and major recommendations, persist them, mark session completed.
    Idempotent: calling again on a completed session returns the cached result.
    """
    session = await assessment_repo.get_session_with_relations(db, session_id)
    if not session:
        raise SessionNotFoundError(session_id)

    # 幂等：已完成直接返回缓存结果
    if session.status == "completed":
        major_map = await _load_major_map(db, session)
        return _build_result(session, major_map)

    # ── 校验所有题目已作答 ────────────────────────────────────────────────
    riasec_responses = {
        r.question_id: r.answer
        for r in session.responses
        if r.module == "riasec"
    }
    if len(riasec_responses) < len(RIASEC_QUESTION_MAP):
        raise InsufficientResponsesError(
            answered=len(riasec_responses),
            required=len(RIASEC_QUESTION_MAP),
        )

    # ── 计算 RIASEC 分数 ──────────────────────────────────────────────────
    scores = compute_riasec(riasec_responses)

    # ── 专业排名 ──────────────────────────────────────────────────────────
    majors = await major_repo.get_active_majors(db)
    profiles = [(str(m.id), m.riasec_vector) for m in majors]
    matches = rank_majors(scores, profiles, top_n=settings.TOP_N_RECOMMENDATIONS)

    # major_map 在循环外准备好，save_completion 里不会产生 N+1 查询
    major_map = {str(m.id): m for m in majors}

    await assessment_repo.save_completion(db, session, scores, matches, major_map)

    return _build_result(session, major_map)


@router.get("/{session_id}/result", response_model=AssessmentResult)
async def get_result(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> AssessmentResult:
    """Retrieve results for a completed session (e.g. for share links)."""
    session = await assessment_repo.get_session_with_relations(db, session_id)
    if not session:
        raise SessionNotFoundError(session_id)
    if session.status != "completed":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Session not completed yet.")

    major_map = await _load_major_map(db, session)
    return _build_result(session, major_map)


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _load_major_map(db: AsyncSession, session: AssessmentSession) -> dict[str, Major]:
    """
    按推荐列表里的 major_id，一次性查出所有需要的专业。
    只查这个 session 实际推荐的专业，不查全表。
    """
    major_ids = [rec.major_id for rec in session.recommendations]
    result = await db.execute(
        select(Major).where(Major.id.in_(major_ids))
    )
    return {str(m.id): m for m in result.scalars()}


def _build_result(session: AssessmentSession, major_map: dict[str, Major]) -> AssessmentResult:
    """
    把 session 里存的分数和推荐记录组装成 API 响应。
    major_map 由调用方传入，这里不查数据库，彻底消除 N+1。
    """
    # 用 RiasecScores 计算 dominant_type 和 top_two，不重复写逻辑
    scores_obj = RiasecScores(
        R=session.score_r or 0,
        I=session.score_i or 0,
        A=session.score_a or 0,
        S=session.score_s or 0,
        E=session.score_e or 0,
        C=session.score_c or 0,
    )

    scores = RiasecScoresOut(
        R=scores_obj.R,
        I=scores_obj.I,
        A=scores_obj.A,
        S=scores_obj.S,
        E=scores_obj.E,
        C=scores_obj.C,
        dominant_type=scores_obj.dominant_type,
        top_two=scores_obj.top_two,
    )

    recs = []
    for rec in sorted(session.recommendations, key=lambda r: r.rank):
        major = major_map.get(str(rec.major_id))
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
