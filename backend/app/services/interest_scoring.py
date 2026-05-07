"""
Interest scoring via Plackett-Luce preference learning.
Pure functions — no DB or HTTP imports.

Two-phase selection:
  Phase 1 (rounds 1-3, coverage): Each round shows 6 categories from 6 different 大类,
    guaranteeing all 18 大类 are seen exactly once after 3 rounds.
  Phase 2 (rounds 4-8, refinement): 1:2 mix — 2 slots from categories the user has
    already selected (highest PL strength first), 4 slots from categories not yet
    selected (highest PL strength first). Allows the model to re-evaluate earlier
    choices and discover overlooked interests.

Stopping: fixed at MAX_ROUNDS = 8. No convergence heuristic — sample size is too
small for reliable convergence detection at this scale.
"""

import math
import random
from dataclasses import dataclass

ALL_CATEGORY_CODES: list[str] = [
    "02", "03", "04", "05", "06",
    "07A", "07B", "07C", "07D", "07E", "07F", "07G", "07H", "07I", "07J",
    "08", "09", "11",
]

N_CATEGORIES = len(ALL_CATEGORY_CODES)   # 18
N_SHOW_PER_ROUND = 6
# With 6 per round, 18 categories need exactly 3 rounds for full coverage.
COVERAGE_ROUNDS = 3
MAX_ROUNDS = 8

# Refinement phase slot allocation (must sum to N_SHOW_PER_ROUND = 6)
# 1:2 exploration ratio — 5 refinement rounds, stay exploration-heavy
N_FROM_SELECTED = 2      # slots for categories the user has already chosen
N_FROM_NON_SELECTED = 4  # slots for categories not yet chosen

_CODE_INDEX: dict[str, int] = {c: i for i, c in enumerate(ALL_CATEGORY_CODES)}


@dataclass(frozen=True)
class InterestRoundData:
    round_number: int
    presented_codes: list[str]
    selected_code: str


def _softmax(values: list[float]) -> list[float]:
    max_v = max(values)
    exp_vals = [math.exp(v - max_v) for v in values]
    total = sum(exp_vals)
    return [e / total for e in exp_vals]


def _compute_strengths(
    rounds: list[InterestRoundData],
    learning_rate: float = 0.4,
    l2_lambda: float = 0.05,
    n_passes: int = 1,
) -> list[float]:
    """
    Estimate log-strength β_i via gradient ascent on Plackett-Luce log-likelihood
    with L2 regularisation.
    """
    strengths = [0.0] * N_CATEGORIES

    for _ in range(n_passes):
        for rd in rounds:
            presented_idx = [_CODE_INDEX[c] for c in rd.presented_codes]
            selected_idx = _CODE_INDEX[rd.selected_code]

            s_vals = [strengths[i] for i in presented_idx]
            probs = _softmax(s_vals)

            for k, idx in enumerate(presented_idx):
                is_winner = 1.0 if idx == selected_idx else 0.0
                grad = is_winner - probs[k] - l2_lambda * strengths[idx]
                strengths[idx] += learning_rate * grad

    return strengths


def compute_interest_scores(rounds: list[InterestRoundData]) -> dict[str, float]:
    """
    Return softmax-normalised interest scores for all 18 categories (sum = 1.0).
    """
    if not rounds:
        uniform = 1.0 / N_CATEGORIES
        return {code: uniform for code in ALL_CATEGORY_CODES}

    strengths = _compute_strengths(rounds, n_passes=3)
    scores = _softmax(strengths)
    return {code: scores[i] for i, code in enumerate(ALL_CATEGORY_CODES)}


def select_next_categories(
    rounds: list[InterestRoundData],
    n_show: int = N_SHOW_PER_ROUND,
) -> list[str]:
    """
    Phase 1 (< COVERAGE_ROUNDS completed): show least-presented 大类 to ensure
    all 18 are covered in exactly 3 rounds.

    Phase 2 (>= COVERAGE_ROUNDS completed): 1:2 mix of selected vs non-selected
    categories, ranked by Plackett-Luce strength within each group.
    """
    if len(rounds) < COVERAGE_ROUNDS:
        return _select_coverage(rounds, n_show)
    return _select_refinement(rounds, n_show)


def _select_coverage(rounds: list[InterestRoundData], n_show: int) -> list[str]:
    """Show the least-presented 大类 first (ties broken randomly)."""
    counts: dict[str, int] = {code: 0 for code in ALL_CATEGORY_CODES}
    for rd in rounds:
        for code in rd.presented_codes:
            counts[code] += 1

    shuffled = list(ALL_CATEGORY_CODES)
    random.shuffle(shuffled)
    shuffled.sort(key=lambda c: counts[c])
    return shuffled[:n_show]


def _select_refinement(rounds: list[InterestRoundData], n_show: int) -> list[str]:
    """
    1:2 mix: N_FROM_SELECTED slots from already-selected categories (exploitation),
    N_FROM_NON_SELECTED slots from not-yet-selected categories (exploration).

    Selected pool  — sorted by PL strength descending: reward confirmed preferences.
    Non-selected pool — sorted by (appearance_count ASC, PL strength DESC): ensure
      every category gets a fair number of exposures before PL scores dominate.
      This prevents high-β losers from monopolising all exploration slots while
      low-exposure categories never get a second chance.
    """
    selected_codes = {rd.selected_code for rd in rounds}
    non_selected = [c for c in ALL_CATEGORY_CODES if c not in selected_codes]

    strengths = _compute_strengths(rounds, n_passes=3)
    strength_map = dict(zip(ALL_CATEGORY_CODES, strengths))

    # Appearance counts across all rounds
    counts: dict[str, int] = {c: 0 for c in ALL_CATEGORY_CODES}
    for rd in rounds:
        for code in rd.presented_codes:
            counts[code] += 1

    # Exploitation: top PL-strength from already-selected pool
    selected_sorted = sorted(selected_codes, key=lambda c: -strength_map[c])

    # Exploration: least-shown first; break ties by PL strength (higher β = better signal)
    non_sorted = sorted(non_selected, key=lambda c: (counts[c], -strength_map[c]))

    n_sel = min(N_FROM_SELECTED, len(selected_sorted))
    n_non = n_show - n_sel

    chosen = selected_sorted[:n_sel] + non_sorted[:n_non]
    random.shuffle(chosen)
    return chosen


def should_stop(rounds: list[InterestRoundData]) -> bool:
    """Fixed 8-round limit. No convergence heuristic."""
    return len(rounds) >= MAX_ROUNDS
