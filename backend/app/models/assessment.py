"""
Assessment session design:
- A session is created the moment the user starts (even before answering).
- Responses are written incrementally so partial progress can be restored.
- Scores are computed and cached in the session row on completion.
- Recommendations are stored so we can A/B test algorithm changes
  without re-running history.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class AssessmentSession(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "assessment_sessions"

    # algorithm version — lets us re-run scoring when weights change
    algorithm_version: Mapped[str] = mapped_column(String(10), default="1.0", nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="in_progress", nullable=False
    )  # in_progress | completed | abandoned
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # ── Cached RIASEC scores (0-100) ─────────────────────────────────────
    # NULL until session is completed
    score_r: Mapped[int | None] = mapped_column(SmallInteger)
    score_i: Mapped[int | None] = mapped_column(SmallInteger)
    score_a: Mapped[int | None] = mapped_column(SmallInteger)
    score_s: Mapped[int | None] = mapped_column(SmallInteger)
    score_e: Mapped[int | None] = mapped_column(SmallInteger)
    score_c: Mapped[int | None] = mapped_column(SmallInteger)

    # ── Relationships ─────────────────────────────────────────────────────
    responses: Mapped[list["AssessmentResponse"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["AssessmentRecommendation"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="AssessmentRecommendation.rank"
    )

    @property
    def riasec_vector(self) -> list[int] | None:
        scores = [self.score_r, self.score_i, self.score_a, self.score_s, self.score_e, self.score_c]
        return scores if all(s is not None for s in scores) else None


class AssessmentResponse(UUIDMixin, Base):
    """One row per question answered. Allows incremental saving and auditing."""

    __tablename__ = "assessment_responses"
    __table_args__ = (UniqueConstraint("session_id", "question_id"),)

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[str] = mapped_column(String(20), nullable=False)
    module: Mapped[str] = mapped_column(String(20), nullable=False)  # riasec | ability | values
    answer: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 1-5
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    session: Mapped["AssessmentSession"] = relationship(back_populates="responses")


class AssessmentRecommendation(UUIDMixin, Base):
    """Persisted ranked recommendations per session."""

    __tablename__ = "assessment_recommendations"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False
    )
    major_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("majors.id"), nullable=False
    )
    rank: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    similarity_score: Mapped[Decimal] = mapped_column(nullable=False)

    session: Mapped["AssessmentSession"] = relationship(back_populates="recommendations")
