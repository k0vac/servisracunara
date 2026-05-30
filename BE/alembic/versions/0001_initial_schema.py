"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "technician", name="userrole", native_enum=False),
            nullable=False,
        ),
        sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "shop_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "shop_name",
            sa.String(length=128),
            nullable=False,
            server_default="PC Repair Service",
        ),
        sa.Column("shop_address", sa.Text(), nullable=True),
        sa.Column("shop_phone", sa.String(length=32), nullable=True),
        sa.Column(
            "default_tax_rate",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column("payment_terms", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticket_number", sa.String(length=32), nullable=False),
        sa.Column("customer_name", sa.String(length=128), nullable=False),
        sa.Column("customer_phone", sa.String(length=32), nullable=False),
        sa.Column("device_type", sa.String(length=64), nullable=False),
        sa.Column("device_brand", sa.String(length=64), nullable=False),
        sa.Column("device_model", sa.String(length=64), nullable=False),
        sa.Column("reported_issue", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "open",
                "in_progress",
                "awaiting_payment",
                "closed",
                name="casestatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.Enum("low", "normal", "urgent", name="casepriority", native_enum=False),
            nullable=False,
        ),
        sa.Column("assigned_to", sa.Integer(), nullable=True),
        sa.Column("estimated_completion", sa.String(length=128), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticket_number"),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "parts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column(
            "unit_price",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column("quantity_on_hand", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("low_stock_threshold", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "case_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum(
                "note",
                "diagnosis",
                "repair",
                "part_used",
                name="caseeventtype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "part_usages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("part_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price_at_time", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("recorded_by", sa.Integer(), nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["part_id"], ["parts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("invoice_number", sa.String(length=32), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("customer_name", sa.String(length=128), nullable=False),
        sa.Column(
            "status",
            sa.Enum("draft", "issued", "paid", name="invoicestatus", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "subtotal",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "tax_rate",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "tax_amount",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column(
            "total",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_id"),
        sa.UniqueConstraint("invoice_number"),
    )

    op.create_table(
        "invoice_line_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column(
            "quantity",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default="1.00",
        ),
        sa.Column("unit_price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("line_total", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "source",
            sa.Enum(
                "material",
                "labor",
                "fee",
                "discount",
                name="invoicelineitemsource",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("part_usage_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["part_usage_id"], ["part_usages.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("invoice_line_items")
    op.drop_table("invoices")
    op.drop_table("part_usages")
    op.drop_table("case_events")
    op.drop_table("parts")
    op.drop_table("notifications")
    op.drop_table("cases")
    op.drop_table("shop_settings")
    op.drop_table("categories")
    op.drop_table("users")
