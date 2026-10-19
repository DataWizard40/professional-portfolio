"""create tables

Revision ID: 0001
Revises:
Create Date: 2026-10-19 16:03:43.918033
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("isbn", sa.String(length=13), nullable=False),
        sa.Column("published_year", sa.Integer(), nullable=True),
        sa.Column("total_copies", sa.Integer(), nullable=False),
        sa.Column("available_copies", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "available_copies <= total_copies", name="ck_books_available_not_above_total"
        ),
        sa.CheckConstraint("available_copies >= 0", name="ck_books_available_not_negative"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("isbn"),
    )
    op.create_index(op.f("ix_books_author"), "books", ["author"], unique=False)
    op.create_index(op.f("ix_books_title"), "books", ["title"], unique=False)
    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("joined_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "loans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("borrowed_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("returned_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
        ),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_loans_member_returned", "loans", ["member_id", "returned_at"], unique=False)


def downgrade() -> None:
    op.drop_table("loans")
    op.drop_table("members")
    op.drop_table("books")
