import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class AssessmentSession(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "assessment_sessions"

    algorithm_version: Mapped[str] = mapped_column(String(10), default="2.0", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    score_r: Mapped[int | None] = mapped_column(SmallInteger)
    score_i: Mapped[int | None] = mapped_column(SmallInteger)
    score_a: Mapped[int | None] = mapped_column(SmallInteger)
    score_s: Mapped[int | None] = mapped_column(SmallInteger)
    score_e: Mapped[int | None] = mapped_column(SmallInteger)
    score_c: Mapped[int | None] = mapped_column(SmallInteger)

    interest_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    responses: Mapped[list["AssessmentResponse"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["AssessmentRecommendation"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="AssessmentRecommendation.rank"
    )
    interest_rounds: Mapped[list["InterestRound"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="InterestRound.round_number"
    )

    @property
    def riasec_vector(self) -> list[int] | None:
        scores = [self.score_r, self.score_i, self.score_a, self.score_s, self.score_e, self.score_c]
        return scores if all(s is not None for s in scores) else None


class AssessmentResponse(UUIDMixin, Base):
    __tablename__ = "assessment_responses"
    __table_args__ = (UniqueConstraint("session_id", "question_id"),)

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[str] = mapped_column(String(20), nullable=False)
    module: Mapped[str] = mapped_column(String(20), nullable=False)
    answer: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    session: Mapped["AssessmentSession"] = relationship(back_populates="responses")


class InterestRound(UUIDMixin, Base):
    __tablename__ = "interest_rounds"
    __table_args__ = (UniqueConstraint("session_id", "round_number", name="uq_interest_session_round"),)

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    presented_category_codes: Mapped[list] = mapped_column(JSONB, nullable=False)
    presented_sample_codes: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    selected_category_code: Mapped[str] = mapped_column(String(10), nullable=False)

    session: Mapped["AssessmentSession"] = relationship(back_populates="interest_rounds")


class AssessmentRecommendation(UUIDMixin, Base):
    __tablename__ = "assessment_recommendations"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False
    )
    major_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("majors.id"), nullable=False)
    rank: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    similarity_score: Mapped[Decimal] = mapped_column(nullable=False)
    interest_score: Mapped[Decimal | None] = mapped_column(nullable=True)
    combined_score: Mapped[Decimal | None] = mapped_column(nullable=True)
    is_conflict: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    session: Mapped["AssessmentSession"] = relationship(back_populates="recommendations")
