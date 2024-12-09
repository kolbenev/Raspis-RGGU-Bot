import asyncio
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
import locale
from datetime import datetime, timedelta

from bot.utils.utils import lazy_get_user_by_chat_id, get_user_with_group_and_schedule_by_chat_id
from database.confdb import session
from database.models import User, Schedule


from typing import List
from collections import defaultdict


def formatter_schedule(list_schedule: List[Schedule]) -> str:
    schedule_dict = defaultdict(list)
    for line in list_schedule:
        key = (line.date, line.para, line.lecture_time)
        schedule_dict[key].append(line)

    done_string = ""
    for (date, para, lecture_time), lessons in schedule_dict.items():
        done_string += f"{date} {para} ({lecture_time}):\n"
        for lesson in lessons:
            done_string += f"  {lesson.lesson} ({lesson.type_lesson}) - ауд. {lesson.audience}, преподаватель: {lesson.teacher_name}\n"
        done_string += "\n"

    return done_string.strip()


async def get_today_schedule(session: AsyncSession, chat_id: int) -> str:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d.%m.%Y %a").upper()

    user: User = await get_user_with_group_and_schedule_by_chat_id(chat_id=chat_id, session=session)
    today_schedule = [
        schedule
        for schedule in user.group.schedule
        if schedule.date == formatted_date
    ]

    return formatter_schedule(today_schedule)


async def get_tomorrow_schedule(session: AsyncSession, chat_id: int) -> str:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    tomorrow_date = datetime.now() + timedelta(days=1)
    formatted_date = tomorrow_date.strftime("%d.%m.%Y %a").upper()

    user: User = await get_user_with_group_and_schedule_by_chat_id(chat_id=chat_id, session=session)
    tomorrow_schedule = [
        schedule
        for schedule in user.group.schedule
        if schedule.date == formatted_date
    ]

    return formatter_schedule(tomorrow_schedule)