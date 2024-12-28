"""
Панель пользователя.
"""

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.handlers.registration import start_registration
from bot.utils.other.keyboards import admin_kb, student_kb
from bot.utils.other.text_for_messages import welcome_messages
from bot.utils.utils import lazy_get_user_by_chat_id
from database.confdb import session
from bot.utils.other.logger import logger
from bot.utils.schedule.getters_schedule import (
    get_today_schedule,
    get_tomorrow_schedule,
    get_weekly_schedule,
)
from database.models import User

router = Router(name=__name__)


@router.message(F.text == "📌 На сегодня")
async def schedule_for_today(message: Message) -> None:
    schedule: str = await get_today_schedule(session=session, chat_id=message.chat.id)
    await message.answer(text=schedule)
    logger.info(
        f"{message.chat.username}:{message.chat.id} получил расписание на сегодня."
    )


@router.message(F.text == "🌅 На завтра")
async def schedule_for_today(message: Message) -> None:
    schedule: str = await get_tomorrow_schedule(
        session=session, chat_id=message.chat.id
    )
    await message.answer(text=schedule)
    logger.info(
        f"{message.chat.username}:{message.chat.id} получил расписание на завтра."
    )


@router.message(F.text == "📆 На неделю")
async def schedule_for_today(message: Message) -> None:
    schedule: str = await get_weekly_schedule(session=session, chat_id=message.chat.id)
    await message.answer(text=schedule)
    logger.info(
        f"{message.chat.username}:{message.chat.id} получил расписание на неделю."
    )

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"{message.chat.username}:{message.chat.id} ввел /start")
    try:
        user: User = await lazy_get_user_by_chat_id(
            chat_id=message.chat.id, session=session
        )

        if user.admin:
            await message.answer(
                text="Выдана административная панель", reply_markup=admin_kb()
            )
        else:
            await message.answer(
                text=welcome_messages,
                reply_markup=student_kb(),
            )

    except ValueError:
        await start_registration(message=message, state=state)


@router.message(Command("changedata"))
async def command_changedata(message: Message, state: FSMContext) -> None:
    try:
        user: User = await lazy_get_user_by_chat_id(
            chat_id=message.chat.id, session=session
        )
        await session.commit()
    except ValueError:
        pass
    logger.info(f"{message.chat.username}:{message.chat.id} ввел /changedata")
    await start_registration(message=message, state=state)