"""
Модуль проверки прав пользователей.
"""

from functools import wraps

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.middlewares.logger import logger
from bot.utils.utils import lazy_get_user_by_chat_id
from database.confdb import session
from database.models import User


def is_admin(func):
    """
    Декоратор для функции проверяющий является ли
    пользователь администатором.
    """
    @wraps(func)
    async def wrapper(message: Message, state: FSMContext, *args, **kwargs):
        try:
            user: User = await lazy_get_user_by_chat_id(
                chat_id=message.chat.id, session=session
            )

            if user.admin:
                return await func(message, state, *args, **kwargs)

            await message.answer(
                text="Недостаточно прав для использования этой команды"
            )
            logger.warning(
                f"{message.from_user.username}:{message.chat.id} попытался получить доступ к {func.__name__}"
            )
        except ValueError:
            logger.warning(
                f"{message.from_user.username}:{message.chat.id} попытался получить доступ к {func.__name__}, будучи не зарегистрированным."
            )

    return wrapper


def is_registered(func):
    """
    Функция декоратор для проверки зарегистрирован ли
    пользователь.
    """
    @wraps(func)
    async def wrapper(message: Message, state: FSMContext, *args, **kwargs):
        try:
            user: User = await lazy_get_user_by_chat_id(
                chat_id=message.chat.id, session=session
            )
            return await func(message, state, *args, **kwargs)
        except ValueError:
            await message.answer(
                text="Вы не зарегистрированны, введите комманду /start"
            )
            f"{message.from_user.username}:{message.chat.id} попытался получить доступ к {func.__name__}, будучи не зарегистрированным."

    return wrapper
