"""
Tests for app/services/scoring.py

Run with: pytest tests/test_scoring.py -v
"""

import pytest

from app.services.scoring import (
    MajorMatch,
    RiasecScores,
    compute_riasec,
    cosine_similarity,
    rank_majors,
)


class TestComputeRiasec:
    def test_all_max_answers_gives_100(self):
        responses = {f"{t.lower()}{i}": 5 for t in "RIASEC" for i in [1, 2]}
        scores = compute_riasec(responses)
        assert scores.R == 100
        assert scores.I == 100

    def test_all_min_answers_gives_50(self):
        # min raw = 2 questions × 1 = 2; normalised = 2/10 × 100 = 20
        responses = {f"{t.lower()}{i}": 1 for t in "RIASEC" for i in [1, 2]}
        scores = compute_riasec(responses)
        assert scores.R == 20

    def test_unknown_question_id_is_ignored(self):
        responses = {"r1": 5, "r2": 5, "unknown_q": 5}
        scores = compute_riasec(responses)
        assert scores.R == 100  # only r1 + r2 counted

    def test_missing_questions_default_to_3(self):
        # r1 answered (5), r2 missing → raw R = 5 + 3 = 8 → 80
        scores = compute_riasec({"r1": 5})
        assert scores.R == 80

    def test_dominant_type(self):
        responses = {f"{t.lower()}{i}": (5 if t == "I" else 1) for t in "RIASEC" for i in [1, 2]}
        scores = compute_riasec(responses)
        assert scores.dominant_type == "I"

    def test_top_two(self):
        responses = {f"{t.lower()}{i}": (5 if t in ("I", "C") else 1) for t in "RIASEC" for i in [1, 2]}
        scores = compute_riasec(responses)
        assert set(scores.top_two) == {"I", "C"}


class TestCosineSimilarity:
    def test_identical_vectors_return_1(self):
        v = [0.8, 0.2, 0.1, 0.3, 0.5, 0.4]
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors_return_0(self):
        a = [1.0, 0, 0, 0, 0, 0]
        b = [0, 1.0, 0, 0, 0, 0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_zero_vector_returns_0(self):
        assert cosine_similarity([0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1]) == 0.0


class TestRankMajors:
    PROFILES = [
        ("cs-id",      [0.4, 0.9, 0.2, 0.1, 0.3, 0.6]),  # 计算机
        ("social-id",  [0.1, 0.4, 0.3, 0.9, 0.5, 0.4]),  # 社会工作
        ("design-id",  [0.4, 0.3, 0.9, 0.3, 0.5, 0.4]),  # 设计
    ]

    def test_investigative_user_prefers_cs(self):
        scores = RiasecScores(R=30, I=95, A=20, S=15, E=30, C=60)
        matches = rank_majors(scores, self.PROFILES, top_n=3)
        assert matches[0].major_id == "cs-id"

    def test_social_user_prefers_social_work(self):
        scores = RiasecScores(R=10, I=40, A=30, S=90, E=50, C=40)
        matches = rank_majors(scores, self.PROFILES, top_n=3)
        assert matches[0].major_id == "social-id"

    def test_returns_correct_number_of_results(self):
        scores = RiasecScores(R=50, I=50, A=50, S=50, E=50, C=50)
        assert len(rank_majors(scores, self.PROFILES, top_n=2)) == 2

    def test_ranks_are_sequential(self):
        scores = RiasecScores(R=50, I=50, A=50, S=50, E=50, C=50)
        matches = rank_majors(scores, self.PROFILES)
        assert [m.rank for m in matches] == list(range(1, len(matches) + 1))

    def test_similarity_descending(self):
        scores = RiasecScores(R=50, I=50, A=50, S=50, E=50, C=50)
        matches = rank_majors(scores, self.PROFILES)
        sims = [m.similarity for m in matches]
        assert sims == sorted(sims, reverse=True)
