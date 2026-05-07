"""add presented_sample_codes to interest_rounds

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-06
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interest_rounds",
        sa.Column("presented_sample_codes", JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("interest_rounds", "presented_sample_codes")
