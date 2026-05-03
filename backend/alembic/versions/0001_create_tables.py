"""create tables

Revision ID: 0001
Revises:
Create Date: 2026-05-02
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "majors",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("discipline_category", sa.String(50), nullable=False),
        sa.Column("major_category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("riasec_r", sa.Numeric(3, 2), nullable=False),
        sa.Column("riasec_i", sa.Numeric(3, 2), nullable=False),
        sa.Column("riasec_a", sa.Numeric(3, 2), nullable=False),
        sa.Column("riasec_s", sa.Numeric(3, 2), nullable=False),
        sa.Column("riasec_e", sa.Numeric(3, 2), nullable=False),
        sa.Column("riasec_c", sa.Numeric(3, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "assessment_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_progress"),
        sa.Column("algorithm_version", sa.String(20), nullable=False, server_default="v1"),
        sa.Column("score_r", sa.Integer, nullable=True),
        sa.Column("score_i", sa.Integer, nullable=True),
        sa.Column("score_a", sa.Integer, nullable=True),
        sa.Column("score_s", sa.Integer, nullable=True),
        sa.Column("score_e", sa.Integer, nullable=True),
        sa.Column("score_c", sa.Integer, nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "assessment_responses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("assessment_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("module", sa.String(20), nullable=False),
        sa.Column("question_id", sa.String(20), nullable=False),
        sa.Column("answer", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("session_id", "question_id", name="uq_response_session_question"),
    )

    op.create_table(
        "assessment_recommendations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("assessment_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "major_id",
            UUID(as_uuid=True),
            sa.ForeignKey("majors.id"),
            nullable=False,
        ),
        sa.Column("rank", sa.Integer, nullable=False),
        sa.Column("similarity_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    # 删除顺序和建表顺序相反，先删有外键依赖的表
    op.drop_table("assessment_recommendations")
    op.drop_table("assessment_responses")
    op.drop_table("assessment_sessions")
    op.drop_table("majors")
