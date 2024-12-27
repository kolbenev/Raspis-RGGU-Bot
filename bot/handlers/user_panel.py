"""
Панель пользователя.
"""

from aiogram import Router, F
from aiogram.types import Message

from database.confdb import session
from bot.utils.other.logger import logger
from bot.utils.schedule.getters_schedule import (
    get_today_schedule,
    get_tomorrow_schedule,
    get_weekly_schedule,
)


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
