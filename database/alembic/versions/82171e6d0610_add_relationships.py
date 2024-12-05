"""add relationships

Revision ID: 82171e6d0610
Revises: ea05bc65624a
Create Date: 2024-12-05 19:34:43.636191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82171e6d0610'
down_revision: Union[str, None] = 'ea05bc65624a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Преобразование типа столбца с указанием USING
    op.alter_column(
        'users',
        'gruppa',
        existing_type=sa.VARCHAR(),
        type_=sa.Integer(),
        nullable=False,
        postgresql_using='gruppa::integer'
    )

    # Создание внешнего ключа
    op.create_foreign_key(
        'fk_users_gruppa',  # Имя внешнего ключа
        'users',  # Таблица, в которой добавляем внешний ключ
        'groups',  # Таблица, на которую ссылаемся
        ['gruppa'],  # Поле в таблице `users`
        ['id']  # Поле в таблице `groups`
    )


def downgrade() -> None:
    # Удаление внешнего ключа
    op.drop_constraint('fk_users_gruppa', 'users', type_='foreignkey')

    # Обратное изменение типа столбца
    op.alter_column(
        'users',
        'gruppa',
        existing_type=sa.Integer(),
        type_=sa.VARCHAR(),
        nullable=True
    )

