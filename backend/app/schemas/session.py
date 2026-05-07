import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Session creation ──────────────────────────────────────────────────────────

class SessionCreated(BaseModel):
    session_id: uuid.UUID
    algorithm_version: str


# ── RIASEC responses ──────────────────────────────────────────────────────────

class ResponseItem(BaseModel):
    question_id: str
    module: str
    answer: int = Field(ge=1, le=5)
    answered_at: datetime | None = None


class SubmitResponsesRequest(BaseModel):
    responses: list[ResponseItem]


# ── Interest selection ────────────────────────────────────────────────────────

class SampleMajorCategory(BaseModel):
    """一个专业类的展示信息，作为兴趣选项的内容。"""
    code: str
    name: str
    description: str
    typical_representatives: str


class InterestOption(BaseModel):
    """兴趣选择一轮中的一个选项：大类 + 该大类下随机抽取的一个专业类。"""
    category_code: str
    category_name: str
    sample: SampleMajorCategory


class InterestRoundResponse(BaseModel):
    round_number: int
    options: list[InterestOption]


class InterestSubmitRequest(BaseModel):
    round_number: int
    selected_category_code: str
    presented_category_codes: list[str]
    presented_sample_codes: list[str]


class InterestSubmitResponse(BaseModel):
    should_stop: bool
    next_round: InterestRoundResponse | None = None


# ── Result ────────────────────────────────────────────────────────────────────

class RiasecScoresOut(BaseModel):
    R: int
    I: int
    A: int
    S: int
    E: int
    C: int
    dominant_type: str
    top_two: tuple[str, str]


class MajorSummary(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    discipline_category: str
    major_category: str
    description: str | None = None


class SubMajorItem(BaseModel):
    code: str
    name: str


class RecommendationItem(BaseModel):
    rank: int
    similarity_score: float
    interest_score: float | None = None
    combined_score: float | None = None
    is_conflict: bool = False
    major: MajorSummary
    sub_majors: list[SubMajorItem] = []


class AssessmentResult(BaseModel):
    session_id: uuid.UUID
    riasec_scores: RiasecScoresOut
    interest_scores: dict[str, float] | None = None
    recommendations: list[RecommendationItem]
    completed_at: datetime
