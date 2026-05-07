import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assessment import (
    AssessmentRecommendation,
    AssessmentResponse,
    AssessmentSession,
    InterestRound,
)
from app.models.major import Major
from app.schemas.session import InterestSubmitRequest, ResponseItem
from app.services.scoring import MajorMatch, RiasecScores


async def create_session(db: AsyncSession) -> AssessmentSession:
    session = AssessmentSession()
    db.add(session)
    await db.flush()
    return session


async def get_session(db: AsyncSession, session_id: uuid.UUID) -> AssessmentSession | None:
    return await db.get(AssessmentSession, session_id)


async def get_session_with_relations(
    db: AsyncSession, session_id: uuid.UUID
) -> AssessmentSession | None:
    result = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.id == session_id)
        .options(
            selectinload(AssessmentSession.responses),
            selectinload(AssessmentSession.recommendations),
            selectinload(AssessmentSession.interest_rounds),
        )
    )
    return result.scalar_one_or_none()


async def get_interest_rounds(
    db: AsyncSession, session_id: uuid.UUID
) -> list[InterestRound]:
    result = await db.execute(
        select(InterestRound)
        .where(InterestRound.session_id == session_id)
        .order_by(InterestRound.round_number)
    )
    return list(result.scalars().all())


async def add_interest_round(
    db: AsyncSession,
    session_id: uuid.UUID,
    body: InterestSubmitRequest,
    presented_codes: list[str],
    presented_sample_codes: list[str],
) -> InterestRound:
    round_obj = InterestRound(
        session_id=session_id,
        round_number=body.round_number,
        presented_category_codes=presented_codes,
        presented_sample_codes=presented_sample_codes,
        selected_category_code=body.selected_category_code,
    )
    db.add(round_obj)
    await db.flush()
    return round_obj


async def get_responses_map(
    db: AsyncSession, session_id: uuid.UUID
) -> dict[str, AssessmentResponse]:
    result = await db.execute(
        select(AssessmentResponse).where(AssessmentResponse.session_id == session_id)
    )
    return {r.question_id: r for r in result.scalars()}


async def upsert_responses(
    db: AsyncSession,
    session_id: uuid.UUID,
    items: list[ResponseItem],
) -> None:
    existing = await get_responses_map(db, session_id)
    for item in items:
        if item.question_id in existing:
            existing[item.question_id].answer = item.answer
        else:
            db.add(AssessmentResponse(
                session_id=session_id,
                question_id=item.question_id,
                module=item.module,
                answer=item.answer,
            ))


async def save_completion(
    db: AsyncSession,
    session: AssessmentSession,
    scores: RiasecScores,
    matches: list[MajorMatch],
    interest_scores: dict[str, float] | None,
    major_map: dict[str, Major],
) -> None:
    session.score_r = scores.R
    session.score_i = scores.I
    session.score_a = scores.A
    session.score_s = scores.S
    session.score_e = scores.E
    session.score_c = scores.C
    session.interest_scores = interest_scores

    for match in matches:
        db.add(AssessmentRecommendation(
            session_id=session.id,
            major_id=uuid.UUID(match.major_id),
            rank=match.rank,
            similarity_score=match.similarity,
            interest_score=match.interest_score,
            combined_score=match.combined_score,
            is_conflict=match.is_conflict,
        ))

    session.status = "completed"
    session.completed_at = datetime.now(UTC)
    await db.flush()
