"""initial schema

Revision ID: 0002_labor_and_repair_links
Revises: 0001_initial_schema
Create Date: 2026-05-31

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_labor_and_repair_links"
down_revision: Union[str, Sequence[str], None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "labor_types",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("hourly_rate", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.add_column("part_usages", sa.Column("case_event_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_part_usages_case_event_id",
        "part_usages",
        "case_events",
        ["case_event_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "case_labor",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("case_event_id", sa.Integer(), nullable=False),
        sa.Column("labor_type_id", sa.Integer(), nullable=False),
        sa.Column("hours", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("rate_at_time", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("recorded_by", sa.Integer(), nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["case_event_id"], ["case_events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["labor_type_id"], ["labor_types.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("case_labor")
    op.drop_constraint("fk_part_usages_case_event_id", "part_usages", type_="foreignkey")
    op.drop_column("part_usages", "case_event_id")
    op.drop_table("labor_types")
