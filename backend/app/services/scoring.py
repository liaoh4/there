"""
Scoring service — pure functions, no DB or HTTP imports.

Pure functions 的好处：单元测试不需要启动数据库或 HTTP 服务器，
直接调用函数传入数据，验证输出即可。
"""

import math
from dataclasses import dataclass
from typing import TypeAlias

RiasecVector: TypeAlias = list[float]

# 题目编号 → RIASEC 维度的映射
RIASEC_QUESTION_MAP: dict[str, str] = {
    "r1": "R", "r2": "R",
    "i1": "I", "i2": "I",
    "a1": "A", "a2": "A",
    "s1": "S", "s2": "S",
    "e1": "E", "e2": "E",
    "c1": "C", "c2": "C",
}

QUESTIONS_PER_DIM = 2        # 每个维度有几道题
RIASEC_MAX_RAW = QUESTIONS_PER_DIM * 5  # 满分原始分 = 题数 × 最高选项


@dataclass(frozen=True)
class RiasecScores:
    R: int
    I: int
    A: int
    S: int
    E: int
    C: int

    def as_vector(self) -> RiasecVector:
        return [self.R, self.I, self.A, self.S, self.E, self.C]

    def as_normalised(self) -> RiasecVector:
        """返回 0-1 归一化向量，供余弦相似度计算使用。"""
        return [v / 100 for v in self.as_vector()]

    @property
    def dominant_type(self) -> str:
        """得分最高的维度。"""
        dims = {"R": self.R, "I": self.I, "A": self.A, "S": self.S, "E": self.E, "C": self.C}
        return max(dims, key=lambda k: dims[k])

    @property
    def top_two(self) -> tuple[str, str]:
        """得分最高的两个维度，从高到低排列。"""
        dims = {"R": self.R, "I": self.I, "A": self.A, "S": self.S, "E": self.E, "C": self.C}
        sorted_dims = sorted(dims, key=lambda k: dims[k], reverse=True)
        return sorted_dims[0], sorted_dims[1]


def compute_riasec(responses: dict[str, int]) -> RiasecScores:
    """
    把答题结果转换为 0-100 的 RIASEC 六维分数。
    调用方需确保所有题目都已作答，此函数不做题目完整性校验。

    Args:
        responses: {question_id: answer (1-5)}
    """
    raw: dict[str, int] = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}

    for qid, ans in responses.items():
        dim = RIASEC_QUESTION_MAP.get(qid)
        if dim:
            raw[dim] += ans

    return RiasecScores(
        **{dim: round(raw[dim] / RIASEC_MAX_RAW * 100) for dim in raw}
    )


@dataclass(frozen=True)
class MajorMatch:
    major_id: str
    similarity: float
    rank: int


def cosine_similarity(a: RiasecVector, b: RiasecVector) -> float:
    """两个向量的余弦相似度，值域 0-1，越接近 1 表示方向越相似。"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rank_majors(
    user_scores: RiasecScores,
    major_profiles: list[tuple[str, RiasecVector]],
    top_n: int = 8,
) -> list[MajorMatch]:
    """
    用余弦相似度对专业排名，返回与用户 RIASEC 向量最接近的 top_n 个专业。

    Args:
        user_scores:    用户的 RIASEC 分数
        major_profiles: [(major_id, [R,I,A,S,E,C]), ...]
        top_n:          返回前几名
    """
    user_vec = user_scores.as_normalised()

    scored = [
        (mid, cosine_similarity(user_vec, profile))
        for mid, profile in major_profiles
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [
        MajorMatch(major_id=mid, similarity=round(sim, 4), rank=i + 1)
        for i, (mid, sim) in enumerate(scored[:top_n])
    ]
