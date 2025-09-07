from datetime import datetime

from aiogram import Bot
from sqlalchemy import select

from bot.states import UserStates
from bot.utils.user_utils.scheduler_getter import MOSCOW_TZ
from config.logger import logger
from database.confdb import session
from database.models import User
from aiogram_dialog import BgManagerFactory, ShowMode
from aiogram_dialog import StartMode


async def notifications_tick(bot: Bot, manager_factory: BgManagerFactory) -> None:
    """
    Ежеминутная проверка времени
    и запуск уведомлений для пользователей.
    """
    now_datetime = datetime.now(MOSCOW_TZ)
    current_time_str = now_datetime.strftime("%H:%M")

    try:
        result = await session.execute(
            select(User).where(
                User.notify_enabled.is_(True),
                User.notify_time == current_time_str,
            )
        )
        users = result.scalars().all()

        if not users:
            logger.debug(
                f"notify_tick {current_time_str}: подходящих пользователей нет"
            )
            return

        logger.info(f"notify_tick {current_time_str}: пользователей={len(users)}")

        for user in users:
            try:
                background_manager = manager_factory.bg(
                    user_id=user.user_id, chat_id=user.chat_id, bot=bot
                )
                await background_manager.start(
                    state=UserStates.schedule_tomorrow,
                    mode=StartMode.RESET_STACK,
                    show_mode=ShowMode.DELETE_AND_SEND,
                )
            except Exception as e:
                logger.exception(
                    f"{user.username}:{user.user_id} ошибка запуска диалога: {e!r}"
                )

    except Exception as e:
        logger.exception(f"notify_tick {current_time_str}: общая ошибка тика: {e!r}")
