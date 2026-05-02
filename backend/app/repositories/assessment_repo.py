import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assessment import AssessmentRecommendation, AssessmentResponse, AssessmentSession
from app.models.major import Major
from app.schemas.session import ResponseItem
from app.services.scoring import MajorMatch, RiasecScores


async def create_session(db: AsyncSession) -> AssessmentSession:
    """创建新的测评会话，写入数据库并返回。"""
    session = AssessmentSession()
    db.add(session)
    await db.flush()
    return session


async def get_session(db: AsyncSession, session_id: uuid.UUID) -> AssessmentSession | None:
    """按 ID 查单个会话，找不到返回 None。"""
    return await db.get(AssessmentSession, session_id)


async def get_session_with_relations(
    db: AsyncSession, session_id: uuid.UUID
) -> AssessmentSession | None:
    """
    查会话并预加载关联数据。
    用 selectinload 一次性加载 responses 和 recommendations，避免 N+1 查询。
    """
    result = await db.execute(
        select(AssessmentSession)
        .where(AssessmentSession.id == session_id)
        .options(
            selectinload(AssessmentSession.responses),
            selectinload(AssessmentSession.recommendations),
        )
    )
    return result.scalar_one_or_none()


async def get_responses_map(
    db: AsyncSession, session_id: uuid.UUID
) -> dict[str, AssessmentResponse]:
    """
    查这个 session 已有的答题记录，以 question_id 为 key 返回字典。
    供 upsert_responses 判断"有则更新，无则插入"。
    """
    result = await db.execute(
        select(AssessmentResponse).where(AssessmentResponse.session_id == session_id)
    )
    return {r.question_id: r for r in result.scalars()}


async def upsert_responses(
    db: AsyncSession,
    session_id: uuid.UUID,
    items: list[ResponseItem],
) -> None:
    """
    批量保存答题记录：已答过的题更新答案，没答过的插入新记录。
    解决前端重复提交同一道题的问题。
    """
    existing = await get_responses_map(db, session_id)

    for item in items:
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


async def save_completion(
    db: AsyncSession,
    session: AssessmentSession,
    scores: RiasecScores,
    matches: list[MajorMatch],
    major_map: dict[str, Major],
) -> None:
    """
    写入计算结果：
    1. 把六维分数写进 session
    2. 把推荐专业列表写进 assessment_recommendations
    3. 把 session 状态改为 completed

    major_map 由调用方提前准备好，避免在这里产生 N+1 查询。
    """
    session.score_r = scores.R
    session.score_i = scores.I
    session.score_a = scores.A
    session.score_s = scores.S
    session.score_e = scores.E
    session.score_c = scores.C

    for match in matches:
        db.add(
            AssessmentRecommendation(
                session_id=session.id,
                major_id=uuid.UUID(match.major_id),
                rank=match.rank,
                similarity_score=match.similarity,
            )
        )

    session.status = "completed"
    session.completed_at = datetime.now(UTC)
    await db.flush()
