"""
Assessment endpoints — v2 with two-phase assessment (interest + RIASEC).

POST /sessions                          → create session
GET  /sessions/{id}/interest/next       → get next interest round
POST /sessions/{id}/interest            → submit interest selection
POST /sessions/{id}/responses           → submit RIASEC answers
POST /sessions/{id}/complete            → compute combined result
GET  /sessions/{id}/result              → retrieve cached result
"""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.interpretation import generate_interpretation
from app.config import get_settings
from app.database import get_db
from app.exceptions import InsufficientResponsesError, SessionAbandonedError, SessionNotFoundError
from app.models.assessment import AssessmentSession
from app.models.major import Major
from app.repositories import assessment_repo, category_repo, major_repo
from app.models.category import MajorCategory
from app.schemas.session import (
    AssessmentResult,
    InterestOption,
    InterestRoundResponse,
    InterestSubmitRequest,
    InterestSubmitResponse,
    MajorSummary,
    RecommendationItem,
    RiasecScoresOut,
    SampleMajorCategory,
    SessionCreated,
    SubMajorItem,
    SubmitResponsesRequest,
)
from app.services.interest_scoring import (
    InterestRoundData,
    compute_interest_scores,
    select_next_categories,
    should_stop,
)
from app.services.scoring import RiasecScores, compute_riasec, rank_majors

router = APIRouter(prefix="/sessions", tags=["assessments"])
settings = get_settings()

MIN_RIASEC_QUESTIONS = 6  # minimum per dimension × number of dimensions answered


# ── Session creation ──────────────────────────────────────────────────────────

@router.post("", response_model=SessionCreated, status_code=status.HTTP_201_CREATED)
async def create_session(db: AsyncSession = Depends(get_db)) -> SessionCreated:
    session = await assessment_repo.create_session(db)
    return SessionCreated(session_id=session.id, algorithm_version=session.algorithm_version)


# ── Interest selection ────────────────────────────────────────────────────────

@router.get("/{session_id}/interest/next", response_model=InterestRoundResponse)
async def get_next_interest_round(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> InterestRoundResponse:
    """Return the next set of 6 category options for the interest selection phase."""
    session = await assessment_repo.get_session(db, session_id)
    if not session:
        raise SessionNotFoundError(session_id)
    if session.status == "abandoned":
        raise SessionAbandonedError(session_id)

    rounds = await assessment_repo.get_interest_rounds(db, session_id)
    round_data = [
        InterestRoundData(
            round_number=r.round_number,
            presented_codes=r.presented_category_codes,
            selected_code=r.selected_category_code,
        )
        for r in rounds
    ]

    next_round_number = len(rounds) + 1
    category_codes = select_next_categories(round_data)

    # Collect all 专业类 codes shown in previous rounds to avoid repetition
    shown_samples: set[str] = {
        code
        for r in rounds
        if r.presented_sample_codes
        for code in r.presented_sample_codes
    }

    name_map = await category_repo.get_category_name_map(db)
    samples = await category_repo.get_sample_per_category(
        db, category_codes, exclude_sample_codes=shown_samples
    )

    options: list[InterestOption] = []
    for code in category_codes:
        sample = samples.get(code)
        if not sample:
            continue
        options.append(InterestOption(
            category_code=code,
            category_name=name_map.get(code, code),
            sample=SampleMajorCategory(
                code=sample.code,
                name=sample.name,
                description=sample.description or "",
                typical_representatives=sample.typical_representatives or "",
            ),
        ))

    return InterestRoundResponse(round_number=next_round_number, options=options)


@router.post("/{session_id}/interest", response_model=InterestSubmitResponse)
async def submit_interest_round(
    session_id: uuid.UUID,
    body: InterestSubmitRequest,
    db: AsyncSession = Depends(get_db),
) -> InterestSubmitResponse:
    """Submit one round's selection. Returns next round or stop signal."""
    session = await assessment_repo.get_session(db, session_id)
    if not session:
        raise SessionNotFoundError(session_id)
    if session.status == "abandoned":
        raise SessionAbandonedError(session_id)

    await assessment_repo.add_interest_round(
        db, session_id, body, body.presented_category_codes, body.presented_sample_codes
    )

    all_rounds = await assessment_repo.get_interest_rounds(db, session_id)
    round_data = [
        InterestRoundData(r.round_number, r.presented_category_codes, r.selected_category_code)
        for r in all_rounds
    ]

    if should_stop(round_data):
        return InterestSubmitResponse(should_stop=True)

    # Build next round — exclude all previously shown 专业类 samples
    shown_samples: set[str] = {
        code
        for r in all_rounds
        if r.presented_sample_codes
        for code in r.presented_sample_codes
    }
    next_codes = select_next_categories(round_data)
    name_map = await category_repo.get_category_name_map(db)
    samples = await category_repo.get_sample_per_category(
        db, next_codes, exclude_sample_codes=shown_samples
    )

    options: list[InterestOption] = []
    for code in next_codes:
        sample = samples.get(code)
        if not sample:
            continue
        options.append(InterestOption(
            category_code=code,
            category_name=name_map.get(code, code),
            sample=SampleMajorCategory(
                code=sample.code,
                name=sample.name,
                description=sample.description or "",
                typical_representatives=sample.typical_representatives or "",
            ),
        ))

    next_round = InterestRoundResponse(round_number=len(all_rounds) + 1, options=options)
    return InterestSubmitResponse(should_stop=False, next_round=next_round)


# ── RIASEC responses ──────────────────────────────────────────────────────────

@router.post("/{session_id}/responses", status_code=status.HTTP_204_NO_CONTENT)
async def submit_responses(
    session_id: uuid.UUID,
    body: SubmitResponsesRequest,
    db: AsyncSession = Depends(get_db),
) -> None:
    session = await assessment_repo.get_session(db, session_id)
    if not session:
        raise SessionNotFoundError(session_id)
    if session.status == "abandoned":
        raise SessionAbandonedError(session_id)
    await assessment_repo.upsert_responses(db, session_id, body.responses)


# ── Complete session ──────────────────────────────────────────────────────────

@router.post("/{session_id}/complete", response_model=AssessmentResult)
async def complete_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> AssessmentResult:
    session = await assessment_repo.get_session_with_relations(db, session_id)
    if not session:
        raise SessionNotFoundError(session_id)

    if session.status == "completed":
        major_map = await _load_major_map(db, session)
        return _build_result(session, major_map)

    # Compute interest scores from rounds
    interest_scores: dict[str, float] | None = None
    if session.interest_rounds:
        round_data = [
            InterestRoundData(r.round_number, r.presented_category_codes, r.selected_category_code)
            for r in session.interest_rounds
        ]
        interest_scores = compute_interest_scores(round_data)

    # Validate RIASEC responses
    riasec_responses = {
        r.question_id: r.answer for r in session.responses if r.module == "riasec"
    }
    if len(riasec_responses) < MIN_RIASEC_QUESTIONS:
        raise InsufficientResponsesError(
            answered=len(riasec_responses), required=MIN_RIASEC_QUESTIONS
        )

    scores = compute_riasec(riasec_responses)

    majors = await major_repo.get_active_majors(db)
    # major.code == assessment category code (e.g. "07A", "09")
    profiles = [(str(m.id), m.riasec_vector, m.code) for m in majors]
    matches = rank_majors(scores, profiles, interest_scores, top_n=settings.TOP_N_RECOMMENDATIONS)

    major_map = {str(m.id): m for m in majors}
    await assessment_repo.save_completion(db, session, scores, matches, interest_scores, major_map)

    # Expire the session object so selectinload re-fetches the freshly-written recommendations.
    db.expire(session)
    session = await assessment_repo.get_session_with_relations(db, session_id)
    sub_major_map = await _load_sub_major_map(db, major_map)
    return _build_result(session, major_map, sub_major_map)


# ── Get result ────────────────────────────────────────────────────────────────

@router.get("/{session_id}/result", response_model=AssessmentResult)
async def get_result(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> AssessmentResult:
    session = await assessment_repo.get_session_with_relations(db, session_id)
    if not session:
        raise SessionNotFoundError(session_id)
    if session.status != "completed":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Session not completed yet.")

    major_map = await _load_major_map(db, session)
    sub_major_map = await _load_sub_major_map(db, major_map)
    riasec_scores = {
        "R": session.score_r or 0,
        "I": session.score_i or 0,
        "A": session.score_a or 0,
        "S": session.score_s or 0,
        "E": session.score_e or 0,
        "C": session.score_c or 0,
    }
    recommendations = [
    {"major": {"name": major_map[str(rec.major_id)].name}}
    for rec in session.recommendations
    if str(rec.major_id) in major_map
]
    if not session.ai_interpretation:
        session.ai_interpretation = await generate_interpretation(
            riasec_scores,
            recommendations,
            interest_scores=session.interest_scores
        )
        await db.commit()
    return _build_result(session, major_map, sub_major_map,)


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _load_major_map(db: AsyncSession, session: AssessmentSession) -> dict[str, Major]:
    major_ids = [rec.major_id for rec in session.recommendations]
    result = await db.execute(select(Major).where(Major.id.in_(major_ids)))
    return {str(m.id): m for m in result.scalars()}


async def _load_sub_major_map(
    db: AsyncSession,
    major_map: dict[str, Major],
) -> dict[str, list[MajorCategory]]:
    category_codes = [m.code for m in major_map.values()]
    return await category_repo.get_sub_majors_by_category_codes(db, category_codes)


def _build_result(
    session: AssessmentSession,
    major_map: dict[str, Major],
    sub_major_map: dict[str, list[MajorCategory]] | None = None,
) -> AssessmentResult:
    scores_obj = RiasecScores(
        R=session.score_r or 0,
        I=session.score_i or 0,
        A=session.score_a or 0,
        S=session.score_s or 0,
        E=session.score_e or 0,
        C=session.score_c or 0,
    )
    scores = RiasecScoresOut(
        R=scores_obj.R, I=scores_obj.I, A=scores_obj.A,
        S=scores_obj.S, E=scores_obj.E, C=scores_obj.C,
        dominant_type=scores_obj.dominant_type,
        top_two=scores_obj.top_two,
    )

    recs = []
    for rec in sorted(session.recommendations, key=lambda r: r.rank):
        major = major_map.get(str(rec.major_id))
        if major:
            sub_majors = [
                SubMajorItem(code=sm.code, name=sm.name)
                for sm in (sub_major_map or {}).get(major.code, [])
            ]
            recs.append(RecommendationItem(
                rank=rec.rank,
                similarity_score=float(rec.similarity_score),
                interest_score=float(rec.interest_score) if rec.interest_score is not None else None,
                combined_score=float(rec.combined_score) if rec.combined_score is not None else None,
                is_conflict=rec.is_conflict or False,
                major=MajorSummary(
                    id=major.id,
                    code=major.code,
                    name=major.name,
                    discipline_category=major.discipline_category,
                    major_category=major.major_category,
                    description=major.description,
                ),
                sub_majors=sub_majors,
            ))

    return AssessmentResult(
        session_id=session.id,
        riasec_scores=scores,
        interest_scores=session.interest_scores,
        recommendations=recs,
        completed_at=session.completed_at or datetime.now(UTC),
        ai_interpretation=session.ai_interpretation,
    )
