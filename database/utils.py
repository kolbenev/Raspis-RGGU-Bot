from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from config.logger import logger
from database.models import User


async def get_user_by_user_id(user_id: int, session: AsyncSession) -> User | None:
    try:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.exception(f"Ошибка при получении пользователя user_id={user_id}: {e!r}")
        await session.rollback()
        return None


async def create_new_user(
    chat_id: int,
    user_id: int,
    username: str,
    session: AsyncSession,
    course: str | None = None,
    group_id: str | None = None,
    eduform: str | None = None,
    status: str | None = None,
    teacher_id: str | None = None,
) -> User | None:
    new_user = User(
        chat_id=chat_id,
        user_id=user_id,
        username=username,
        course=course,
        group_id=group_id,
        eduform=eduform,
        status=status,
        teacher_id=teacher_id,
    )
    try:
        session.add(new_user)
        await session.commit()
        return new_user
    except SQLAlchemyError as e:
        logger.exception(
            f"Ошибка при создании пользователя user_id={user_id}, username={username}: {e!r}"
        )
        await session.rollback()
        return None


async def get_all_users(session: AsyncSession) -> Sequence[User]:
    try:
        stmt = select(User)
        result = await session.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.exception(f"Ошибка при получении всех пользователей: {e!r}")
        await session.rollback()
        return []
