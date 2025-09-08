"""
Revision ID: 1d8ab7a2014b
Revises: 28e787bf0b13
Create Date: 2025-08-30 05:29:44.483645
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1d8ab7a2014b"
down_revision: Union[str, Sequence[str], None] = "28e787bf0b13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("notify_time", sa.String(), nullable=True))
    op.add_column("users", sa.Column("notify_enabled", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "notify_enabled")
    op.drop_column("users", "notify_time")
