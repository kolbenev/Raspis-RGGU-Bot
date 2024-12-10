"""changed kaf to caf

Revision ID: a20086d67ca4
Revises: 2a68e2b2b0ec
Create Date: 2024-12-10 19:30:53.680146

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a20086d67ca4"
down_revision: Union[str, None] = "2a68e2b2b0ec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("groups", sa.Column("caf", sa.String(), nullable=True))
    op.drop_column("groups", "kaf")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "groups", sa.Column("kaf", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.drop_column("groups", "caf")
    # ### end Alembic commands ###
