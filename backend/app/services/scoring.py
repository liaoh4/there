"""
Scoring service — pure functions, no DB or HTTP imports.
"""

import math
from dataclasses import dataclass
from typing import TypeAlias

RiasecVector: TypeAlias = list[float]

RIASEC_DIMS = ("R", "I", "A", "S", "E", "C")


def _dim_from_qid(question_id: str) -> str | None:
    """R001 → R, i2 → I, etc. First char (case-insensitive) must be a RIASEC letter."""
    if question_id:
        ch = question_id[0].upper()
        if ch in RIASEC_DIMS:
            return ch
    return None


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
        return [v / 100 for v in self.as_vector()]

    @property
    def dominant_type(self) -> str:
        dims = {d: getattr(self, d) for d in RIASEC_DIMS}
        return max(dims, key=lambda k: dims[k])

    @property
    def top_two(self) -> tuple[str, str]:
        dims = {d: getattr(self, d) for d in RIASEC_DIMS}
        sorted_dims = sorted(dims, key=lambda k: dims[k], reverse=True)
        return sorted_dims[0], sorted_dims[1]


def compute_riasec(responses: dict[str, int]) -> RiasecScores:
    """
    Convert question responses to 0-100 RIASEC scores.
    Question IDs follow the pattern <DIM><number>, e.g. R001, I016.
    Normalises by (number of questions answered per dim × 5).
    """
    raw: dict[str, int] = {d: 0 for d in RIASEC_DIMS}
    count: dict[str, int] = {d: 0 for d in RIASEC_DIMS}

    for qid, ans in responses.items():
        dim = _dim_from_qid(qid)
        if dim:
            raw[dim] += ans
            count[dim] += 1

    scores = {
        dim: (round(raw[dim] / (count[dim] * 5) * 100) if count[dim] > 0 else 0)
        for dim in RIASEC_DIMS
    }
    return RiasecScores(**scores)


@dataclass(frozen=True)
class MajorMatch:
    major_id: str
    similarity: float
    interest_score: float
    combined_score: float
    is_conflict: bool
    rank: int


def cosine_similarity(a: RiasecVector, b: RiasecVector) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rank_majors(
    user_scores: RiasecScores,
    major_profiles: list[tuple[str, RiasecVector, str]],  # (major_id, riasec_vec, category_code)
    interest_scores: dict[str, float] | None,
    top_n: int = 4,
    min_combined_score: float = 0.5,
    riasec_weight: float = 0.6,
) -> list[MajorMatch]:
    """
    Rank majors by combined RIASEC cosine similarity + Plackett-Luce interest score.

    major_profiles: list of (major_id, riasec_vector, assessment_category_code)
    interest_scores: {category_code: score} from Plackett-Luce (None → pure RIASEC)
    riasec_weight: weight of RIASEC similarity vs interest (0.6 / 0.4 default)
    min_combined_score: only include results at or above this threshold
    """
    user_vec = user_scores.as_normalised()
    interest_weight = 1.0 - riasec_weight

    raw_sims = [(mid, cosine_similarity(user_vec, vec), code) for mid, vec, code in major_profiles]

    if interest_scores:
        max_interest = max(interest_scores.values()) or 1.0
        norm_interest = {k: v / max_interest for k, v in interest_scores.items()}
    else:
        norm_interest = {}

    # Normalise RIASEC similarities to [0,1]
    sims_only = [s for _, s, _ in raw_sims]
    max_sim = max(sims_only) or 1.0
    min_sim = min(sims_only)
    sim_range = max_sim - min_sim or 1.0

    scored: list[tuple[str, float, float, float]] = []  # (id, riasec_sim, interest, combined)
    for mid, sim, code in raw_sims:
        norm_sim = (sim - min_sim) / sim_range
        isc = norm_interest.get(code, 0.5) if norm_interest else 0.5
        combined = riasec_weight * norm_sim + interest_weight * isc
        scored.append((mid, sim, isc, combined))

    scored.sort(key=lambda x: x[3], reverse=True)

    # Conflict: high interest but low RIASEC compatibility
    sim_median = sorted(sims_only)[len(sims_only) // 2]

    result = []
    rank = 1
    for mid, sim, isc, combined in scored:
        if len(result) >= top_n:
            break
        if combined < min_combined_score:
            break
        is_conflict = bool(norm_interest) and (isc > 0.7) and (sim < sim_median * 0.85)
        result.append(MajorMatch(
            major_id=mid,
            similarity=round(sim, 4),
            interest_score=round(isc, 4),
            combined_score=round(combined, 4),
            is_conflict=is_conflict,
            rank=rank,
        ))
        rank += 1
    return result
