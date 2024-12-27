"""
Модуль вспомогательных функций.
"""

from sqlalchemy.orm import joinedload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from telebot.types import logger

from database.models import User, Group


async def lazy_get_user_by_chat_id(chat_id: int, session: AsyncSession) -> User:
    """
    Функция для ленивого получения пользователя
    из базы данных по chat_id.

    :param chat_id: ID Чата.
    :param session: Асинхронная сессия.
    :return: Модель пользователя.
    """
    stmt = select(User).where(User.chat_id == chat_id)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        logger.warn(f"lazy_get_user_by_chat_id не нашла пользователя {chat_id}")
        raise ValueError("User not found")
    else:
        return user


async def get_user_with_group_and_schedule_by_chat_id(
    chat_id: int, session: AsyncSession
) -> User:
    """
    Функция для получения пользователя с подгрузкой
    его расписания.

    :param chat_id: ID Чата.
    :param session: Асинхронная сессия.
    :return: Модель пользователя.
    """
    stmt = (
        select(User)
        .where(User.chat_id == chat_id)
        .options(joinedload(User.group).joinedload(Group.schedule))
    )
    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        logger.warn(
            f"get_user_with_group_and_schedule_by_chat_id не нашла пользователя {chat_id}"
        )
        raise ValueError("User not found")
    else:
        return user


async def lazy_get_group_by_name(group_name: str, session: AsyncSession) -> Group:
    """
    Функция для ленивого получения модели
    группы по ее имени.

    :param group_name: Имя группы.
    :param session: Асинхронная сессия.
    :return: Модель группы.
    """
    stmt = select(Group).where(Group.name == group_name)
    result = await session.execute(stmt)
    group = result.scalars().first()

    if not group:
        logger.warn(f"lazy_get_group_by_name не нашла группу {group_name}")
        raise ValueError("Group not found")
    else:
        return group


async def create_new_group(
    name: str, caf: str, kyrs: int, formob: str, session: AsyncSession
) -> Group:
    """
    Функция для создания новой группы.

    :param kyrs: Курс.
    :param formob: Форма обучения.
    :param name: Имя группы.
    :param caf: ID кафедры.
    :param session: Асинхронная сессия.
    :return:
    """
    new_group = Group(
        name=name,
        caf=caf,
        kyrs=kyrs,
        formob=formob,
    )
    logger.info(f"Создана новая группа: {new_group.name}")
    session.add(new_group)
    await session.commit()
    return new_group
