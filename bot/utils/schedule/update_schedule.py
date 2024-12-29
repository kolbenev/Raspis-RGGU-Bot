"""
Модуль для реализации ежедневного обновления расписания.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from bot.middlewares.logger import logger

from database.models import Schedule, Group
from parser.parser_main import parsing_schedule


async def refresh_schedule_data(session: AsyncSession):
    """
    Обновляет расписание, очищая старые данные и загружая новые.

    Функция удаляет все текущие записи в таблице расписаний и
    затем извлекает данные о группах, после чего для каждой группы
    запускается процесс парсинга расписания с использованием её параметров.

    :param session: Асинхронная сессия SQLAlchemy.
    :param chat_id: Ид чата.
    :return: Готовое сообщение для отправки.
    """
    stmt = delete(Schedule)
    await session.execute(stmt)
    await session.commit()
    logger.info("Расписание отчищено.")

    stmt = select(Group)
    result = await session.execute(stmt)
    groups = result.scalars().all()

    for group in groups:
        await parsing_schedule(
            formob=group.formob,
            kyrs=group.kyrs,
            caf=group.caf,
        )
    logger.info("Расписание обновлено.")
