"""
Модуль административной панели.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from database.models import User


async def send_message_to_everyone(
    session: AsyncSession, message: Message, bot: AsyncTeleBot
):
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.scalars().all()

    for user in users:
        await bot.send_message(user.chat_id, message.text)


async def get_count_users(session: AsyncSession) -> int:
    """
    Подсчитывает количество пользователей в базе данных.

    :param session: Асинхронная сессия SQLAlchemy.
    :return: Количество пользователей.
    """
    stmt = select(func.count(User.id))
    result = await session.execute(stmt)
    count = result.scalar()
    return count
