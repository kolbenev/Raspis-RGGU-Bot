"""
Модуль напоминания о расписании на завтра.
"""

from datetime import datetime

from aiogram import Router
from aiogram.types import Message

from bot.middlewares.user_permissions import is_registered
from database.confdb import session
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.middlewares.logger import logger
from bot.handlers.states import UserState
from bot.utils.utils import lazy_get_user_by_chat_id
from bot.utils.other.keyboards import time_kb, student_kb


router = Router()


@router.message(Command("settime"))
@is_registered
async def reminder_sheduler(message: Message, state: FSMContext) -> None:
    """
    Функция запрашивает у пользователя время
    в которое он бы хотел получать расписание.
    """
    await message.answer(
        text="🕙 Выберите или введите время в которое хотите получить расписание:",
        reply_markup=time_kb(),
    )
    await state.set_state(UserState.reminder)


@router.message(UserState.reminder)
async def reminder_sheduler(message: Message, state: FSMContext) -> None:
    """
    Функция обрабатывает время которое ввел
    пользователь и заносит информацию в
    запись о пользователе.
    """
    user_input = message.text.strip()
    user = await lazy_get_user_by_chat_id(chat_id=message.chat.id, session=session)

    if message.text == "Отключить напоминание 😥":
        user.reminder = None
        await session.commit()
        await state.clear()
        await message.answer(
            text="Напоминания отключены ✅",
            reply_markup=student_kb(),
        )
        logger.info(
            f"{message.chat.username}{message.chat.id} отключил напоминание."
        )
        return

    try:
        reminder_time = datetime.strptime(user_input, "%H:%M").time()
    except ValueError:
        await message.answer(
            "Неверный формат времени! Пожалуйста, введите время в формате HH:MM (например, 09:00)."
        )
        logger.info(
            f"{message.chat.username}{message.chat.id} ввел неверный формат времени."
        )
        return

    user.reminder = reminder_time
    await session.commit()

    await message.answer(
        text=f"🎈 Теперь вы будете получать расписание на завтра каждый день в {reminder_time.strftime('%H:%M')}!",
        reply_markup=student_kb(),
    )
    logger.info(
        f"{message.chat.username}{message.chat.id} установил время для получения расписания на {reminder_time}"
    )
    await state.clear()
