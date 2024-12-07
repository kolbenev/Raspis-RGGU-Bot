"""add formob and kyrs in user

Revision ID: 97779abdd3e7
Revises: 64345600f3ae
Create Date: 2024-12-06 03:37:04.413864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97779abdd3e7'
down_revision: Union[str, None] = '64345600f3ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('formob', sa.String(length=1), nullable=False))
    op.add_column('users', sa.Column('kyrs', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'kyrs')
    op.drop_column('users', 'formob')
    # ### end Alembic commands ###
