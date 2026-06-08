"""invoice workflow

Revision ID: 0003_invoice_workflow
Revises: 0002_labor_and_repair_links
Create Date: 2026-05-31

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_invoice_workflow"
down_revision: Union[str, Sequence[str], None] = "0002_labor_and_repair_links"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE invoices SET status = 'pending' WHERE status IN ('draft', 'issued')")
    op.execute("UPDATE invoices SET status = 'cancelled' WHERE status NOT IN ('pending', 'paid', 'cancelled')")

    op.add_column("invoices", sa.Column("created_by", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_invoices_created_by",
        "invoices",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column("invoices", sa.Column("retraction_reason", sa.Text(), nullable=True))
    op.add_column("invoices", sa.Column("retracted_at", sa.DateTime(timezone=True), nullable=True))

    op.add_column("invoice_line_items", sa.Column("case_labor_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_invoice_line_items_case_labor_id",
        "invoice_line_items",
        "case_labor",
        ["case_labor_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_invoice_line_items_case_labor_id", "invoice_line_items", type_="foreignkey")
    op.drop_column("invoice_line_items", "case_labor_id")

    op.drop_column("invoices", "retracted_at")
    op.drop_column("invoices", "retraction_reason")
    op.drop_constraint("fk_invoices_created_by", "invoices", type_="foreignkey")
    op.drop_column("invoices", "created_by")

    op.execute("UPDATE invoices SET status = 'draft' WHERE status = 'pending'")
    op.execute("UPDATE invoices SET status = 'issued' WHERE status = 'cancelled'")
