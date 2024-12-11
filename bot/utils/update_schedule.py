"""
Модуль для реализации ежедневного обновления расписания.
"""

import asyncio
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from telebot.types import logger

from database.models import Schedule, Group
from parser.parser_main import parsing_schedule


async def daily_schedule_updater(session: AsyncSession):
    """
    Обновляет расписание каждый день в 00:01.

    Эта функция работает в бесконечном цикле, ожидает до
    00:01 следующего дня, а затем вызывает функцию обновления
    расписания. Цикл продолжается ежедневно, обеспечивая
    актуальность расписания.

    :param session: Асинхронная сессия SQLAlchemy.
    :param chat_id: Ид чата.
    :return: Готовое сообщение для отправки.
    """
    while True:
        now = datetime.now()
        next_run = (now + timedelta(days=1)).replace(
            hour=0, minute=1, second=0, microsecond=0
        )
        sleep_time = (next_run - now).total_seconds()

        await asyncio.sleep(sleep_time)
        logger.info(f'Расписание обновлено с помощью daily_schedule_updater')
        await refresh_schedule_data(session=session)


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
    logger.info('Расписание отчищено.')

    stmt = select(Group)
    result = await session.execute(stmt)
    groups = result.scalars().all()

    for group in groups:
        await parsing_schedule(
            formob=group.formob,
            kyrs=group.kyrs,
            caf=group.caf,
        )
    logger.info('Расписание обновлено.')
