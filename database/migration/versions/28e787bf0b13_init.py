"""
Revision ID: 28e787bf0b13
Revises:
Create Date: 2025-08-29 22:34:16.327192
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "28e787bf0b13"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("course", sa.String(), nullable=True),
        sa.Column("group_id", sa.String(), nullable=True),
        sa.Column("eduform", sa.String(), nullable=True),
        sa.Column("teacher_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True, comment="student/teacher"),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("users")
