"""invoice status varchar

Revision ID: 0004_invoice_status_varchar
Revises: 0003_invoice_workflow
Create Date: 2026-06-04

"""

from typing import Sequence, Union

from alembic import op

revision: str = "0004_invoice_status_varchar"
down_revision: Union[str, Sequence[str], None] = "0003_invoice_workflow"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE invoices MODIFY COLUMN status VARCHAR(16) NOT NULL")


def downgrade() -> None:
    pass
