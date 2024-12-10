from sqlalchemy.ext.asyncio import AsyncSession

from typing import List
import locale
from datetime import datetime, timedelta
from collections import defaultdict

from database.models import User, Schedule
from bot.utils.utils import get_user_with_group_and_schedule_by_chat_id


def formatter_schedule(list_schedule: List[Schedule]) -> str:
    schedule_dict = defaultdict(list)

    for line in list_schedule:
        key = (line.date, line.para, line.lecture_time)
        schedule_dict[key].append(line)

    result = ""
    current_date = None

    for (date, para, lecture_time), lessons in schedule_dict.items():
        if date != current_date:
            if current_date is not None:
                result += "\n"
            result += f"<b>{date}:</b>\n"
            current_date = date

        result += f"<u>{para}-я пара ({lecture_time}):</u>\n"
        for lesson in lessons:
            result += f"{lesson.lesson} ({lesson.type_lesson}) - ауд: {lesson.audience}\nПреподаватель: {lesson.teacher_name}\n"
        result += "\n"

    return result


async def get_today_schedule(session: AsyncSession, chat_id: int) -> str:
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d.%m.%Y %a").upper()

    user: User = await get_user_with_group_and_schedule_by_chat_id(
        chat_id=chat_id, session=session
    )
    today_schedule = [
        schedule for schedule in user.group.schedule if schedule.date == formatted_date
    ]

    return formatter_schedule(today_schedule)


async def get_tomorrow_schedule(session: AsyncSession, chat_id: int) -> str:
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    tomorrow_date = datetime.now() + timedelta(days=1)
    formatted_date = tomorrow_date.strftime("%d.%m.%Y %a").upper()

    user: User = await get_user_with_group_and_schedule_by_chat_id(
        chat_id=chat_id, session=session
    )
    tomorrow_schedule = [
        schedule for schedule in user.group.schedule if schedule.date == formatted_date
    ]

    return formatter_schedule(tomorrow_schedule)


async def get_weekly_schedule(session: AsyncSession, chat_id: int) -> str:
    user: User = await get_user_with_group_and_schedule_by_chat_id(
        chat_id=chat_id, session=session
    )

    return formatter_schedule(user.group.schedule)
