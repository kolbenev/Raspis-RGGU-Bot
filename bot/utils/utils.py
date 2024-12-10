from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        raise ValueError("User not found")
    else:
        return user


from sqlalchemy.orm import joinedload


async def get_user_with_group_and_schedule_by_chat_id(
    chat_id: int, session: AsyncSession
) -> User:
    stmt = (
        select(User)
        .where(User.chat_id == chat_id)
        .options(joinedload(User.group).joinedload(Group.schedule))
    )
    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise ValueError("User not found")
    else:
        return user


async def lazy_get_group_by_name(group_name: str, session: AsyncSession) -> Group:
    """
    Функция для ленивого получения модели группы
    по ее имени.

    :param group_name: Имя группы.
    :param session: Асинхронная сессия.
    :return: Модель группы.
    """
    stmt = select(Group).where(Group.name == group_name)
    result = await session.execute(stmt)
    group = result.scalars().first()

    if not group:
        raise ValueError("Group not found")
    else:
        return group


async def create_new_group(
    name: str, kaf: str, kyrs: int, formob: str, session: AsyncSession
) -> Group:
    """
    Функция для создания новой группы.

    :param kyrs: Курс студента.
    :param name: Имя группы.
    :param kaf: ID кафедры.
    :param session: Асинхронная сессия.
    :return:
    """
    new_group = Group(
        name=name,
        kaf=kaf,
        kyrs=kyrs,
        formob=formob,
    )
    session.add(new_group)
    await session.commit()
    return new_group
