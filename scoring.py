"""
Scoring service.

Kept as pure functions so it can be tested without a DB connection.
The API layer calls these and then persists the results.
"""

import math
from dataclasses import dataclass
from typing import TypeAlias

RiasecVector: TypeAlias = list[float]

# Question → RIASEC dimension mapping
RIASEC_QUESTION_MAP: dict[str, str] = {
    "r1": "R", "r2": "R",
    "i1": "I", "i2": "I",
    "a1": "A", "a2": "A",
    "s1": "S", "s2": "S",
    "e1": "E", "e2": "E",
    "c1": "C", "c2": "C",
}

# Questions per dimension × max Likert = denominator for normalisation
RIASEC_MAX_RAW = 10  # 2 questions × 5


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
        """Return 0-1 normalised vector for cosine similarity."""
        return [v / 100 for v in self.as_vector()]

    @property
    def dominant_type(self) -> str:
        dims = {"R": self.R, "I": self.I, "A": self.A, "S": self.S, "E": self.E, "C": self.C}
        return max(dims, key=lambda k: dims[k])

    @property
    def top_two(self) -> tuple[str, str]:
        dims = {"R": self.R, "I": self.I, "A": self.A, "S": self.S, "E": self.E, "C": self.C}
        sorted_dims = sorted(dims, key=lambda k: dims[k], reverse=True)
        return sorted_dims[0], sorted_dims[1]


def compute_riasec(responses: dict[str, int]) -> RiasecScores:
    """
    Convert raw question responses → normalised 0-100 RIASEC scores.

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
    """Standard cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rank_majors(
    user_scores: RiasecScores,
    major_profiles: list[tuple[str, RiasecVector]],  # [(major_id, [R,I,A,S,E,C]), ...]
    top_n: int = 8,
) -> list[MajorMatch]:
    """
    Rank majors by cosine similarity to user's RIASEC vector.

    Args:
        user_scores:    computed RIASEC scores
        major_profiles: list of (major_id, normalised_riasec_vector) tuples
        top_n:          how many results to return

    Returns:
        Ranked list of MajorMatch, highest similarity first.
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
