from datetime import datetime

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from bot.middlewares.logger import logger
from bot.utils.schedule.getters_schedule import get_tomorrow_schedule


async def remind_schedule(session: AsyncSession, bot: Bot) -> None:
    now = datetime.now().replace(microsecond=0, second=0)
    current_time = now.time()

    stmt = select(User).filter(User.reminder == current_time)
    result = await session.execute(stmt)
    users = result.scalars().all()

    for user in users:
        chat_id = user.chat_id
        schedule = await get_tomorrow_schedule(chat_id=chat_id, session=session)
        await bot.send_message(
            chat_id=chat_id,
            text=schedule,
        )
        logger.info(f"{chat_id} получил расписание как напоминание.")
