"""add interest selection tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-04
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "major_categories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(10), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("assessment_category_code", sa.String(10), nullable=False),
        sa.Column("assessment_category_name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("typical_representatives", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_major_categories_assessment_code", "major_categories", ["assessment_category_code"])

    op.create_table(
        "interest_rounds",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("assessment_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("round_number", sa.Integer, nullable=False),
        sa.Column("presented_category_codes", JSONB, nullable=False),
        sa.Column("selected_category_code", sa.String(10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("session_id", "round_number", name="uq_interest_session_round"),
    )
    op.create_index("ix_interest_rounds_session_id", "interest_rounds", ["session_id"])

    op.add_column("assessment_sessions", sa.Column("interest_scores", JSONB, nullable=True))

    op.add_column("assessment_recommendations", sa.Column("interest_score", sa.Numeric(5, 4), nullable=True))
    op.add_column("assessment_recommendations", sa.Column("combined_score", sa.Numeric(5, 4), nullable=True))
    op.add_column("assessment_recommendations", sa.Column("is_conflict", sa.Boolean, nullable=True, server_default="false"))


def downgrade() -> None:
    op.drop_column("assessment_recommendations", "is_conflict")
    op.drop_column("assessment_recommendations", "combined_score")
    op.drop_column("assessment_recommendations", "interest_score")
    op.drop_column("assessment_sessions", "interest_scores")
    op.drop_index("ix_interest_rounds_session_id", table_name="interest_rounds")
    op.drop_table("interest_rounds")
    op.drop_index("ix_major_categories_assessment_code", table_name="major_categories")
    op.drop_table("major_categories")
