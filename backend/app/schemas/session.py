import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── 第一步：创建 session ──────────────────────────────────────────────────────

class SessionCreated(BaseModel):
    """POST /sessions 的响应：后端返回给前端的 session 编号。"""
    session_id: uuid.UUID
    algorithm_version: str


# ── 第二步：提交答题 ──────────────────────────────────────────────────────────

class ResponseItem(BaseModel):
    """一道题的答案。"""
    question_id: str                        # 题目编号，如 "r1"、"i2"
    module: str                             # 所属模块，目前只有 "riasec"
    answer: int = Field(ge=1, le=5)         # Likert 分值，必须在 1-5 之间
    answered_at: datetime | None = None     # 答题时间，可选


class SubmitResponsesRequest(BaseModel):
    """POST /sessions/{id}/responses 的请求体：打包提交多道题的答案。"""
    responses: list[ResponseItem]


# ── 第三步：完成测评，返回结果 ────────────────────────────────────────────────

class RiasecScoresOut(BaseModel):
    """六维 RIASEC 分数，0-100，返回给前端用于画雷达图。"""
    R: int
    I: int
    A: int
    S: int
    E: int
    C: int
    dominant_type: str          # 得分最高的维度，如 "I"
    top_two: tuple[str, str]    # 得分最高的两个维度，如 ("I", "C")


class MajorSummary(BaseModel):
    """推荐结果里每个专业的简要信息，不暴露 RIASEC profile 等内部数据。"""
    id: uuid.UUID
    code: str
    name: str
    discipline_category: str
    major_category: str


class RecommendationItem(BaseModel):
    """一条推荐记录：排名 + 相似度 + 专业简介。"""
    rank: int
    similarity_score: float
    major: MajorSummary         # 嵌套结构：一条推荐里包含专业信息


class AssessmentResult(BaseModel):
    """POST /sessions/{id}/complete 和 GET /sessions/{id}/result 的响应。"""
    session_id: uuid.UUID
    riasec_scores: RiasecScoresOut
    recommendations: list[RecommendationItem]
    completed_at: datetime
