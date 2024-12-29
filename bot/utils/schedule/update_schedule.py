"""
Модуль для реализации ежедневного обновления расписания.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, case, func, exists
from bot.middlewares.logger import logger

from database.models import Schedule, Group, User
from parser.parser_main import parsing_schedule


async def refresh_schedule_data(session: AsyncSession):
    """
    Обновляет расписание, очищая старые данные и загружая новые.

    Функция удаляет все текущие записи в таблице расписаний и
    затем извлекает данные о группах, после чего для каждой группы
    запускается процесс парсинга расписания с использованием её параметров.
    """

    await session.execute(delete(Schedule))
    logger.info("Старые данные расписания удалены.")

    await session.execute(
        delete(Group).where(~exists(select(User.id).where(User.gruppa == Group.id)))
    )
    logger.info("Группы без пользователей удалены.")
    await session.commit()

    groups = (
        (await session.execute(select(Group)))
        .scalars()
        .all()
    )

    for group in groups:
        await parsing_schedule(group.formob, group.kyrs, group.caf)

    logger.info("Данные расписания обновлены.")
