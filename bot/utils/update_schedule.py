import asyncio
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from database.models import Schedule, Group
from parser.parser_main import parsing_schedule


async def daily_schedule_updater(session: AsyncSession):
    """
    Функция, которая каждый день в 00:00 обновляет расписание.
    """
    while True:
        now = datetime.now()
        next_run = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        sleep_time = (next_run - now).total_seconds()

        await asyncio.sleep(sleep_time)
        await refresh_schedule_data(session=session)


async def refresh_schedule_data(session: AsyncSession):
    """
    Функция для обновления расписания.
    """
    stmt = delete(Schedule)
    await session.execute(stmt)
    await session.commit()

    stmt = select(Group)
    result = await session.execute(stmt)
    groups = result.scalars().all()

    for group in groups:
        await parsing_schedule(
            formob=group.formob,
            kyrs=group.kyrs,
            caf=group.kaf,
        )
