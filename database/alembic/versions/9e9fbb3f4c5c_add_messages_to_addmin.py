"""add messages to addmin

Revision ID: 9e9fbb3f4c5c
Revises: 97764943f19a
Create Date: 2024-12-28 18:53:16.519708

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9e9fbb3f4c5c"
down_revision: Union[str, None] = "97764943f19a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "messages_to_admin",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("date_time", sa.DateTime(), nullable=True),
        sa.Column("messages", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("messages_to_admin")
    # ### end Alembic commands ###