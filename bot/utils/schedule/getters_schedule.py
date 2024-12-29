"""
Модуль для формирования расписания для пользователя.
"""

from typing import List
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Schedule
from bot.utils.utils import get_user_with_group_and_schedule_by_chat_id


days_of_the_week = {
    0: "ПН",
    1: "ВТ",
    2: "СР",
    3: "ЧТ",
    4: "ПТ",
    5: "СБ",
    6: "ВС",
}


def formatter_schedule(list_schedule: List[Schedule]) -> str:
    """
    Форматирует список расписания занятий в строку для вывода пользователю.

    Группирует занятия по дате, парам и времени занятий, формирует текстовый
    блок для каждого дня с информацией о парах, лекциях, аудиториях и преподавателях.
    Текст форматируется с использованием HTML-тегов для выделения информации.

    :param list_schedule: Список моделей расписания.
    :return: Готовое сообщение для отправки.
    """
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

        result += f"<u>{para}-я пара ({lecture_time})" f":</u>\n"
        for lesson in lessons:
            result += f"{lesson.lesson} ({lesson.type_lesson}) - ауд: {lesson.audience}\nПреподаватель: {lesson.teacher_name}\n"
        result += "\n"

    return result


async def get_today_schedule(session: AsyncSession, chat_id: int) -> str:
    """
    Формирует расписание на текущий день для пользователя.

    Функция извлекает текущую дату и на основе её формата ищет занятия
    пользователя на сегодняшний день. Возвращает строку с отформатированным
    расписанием для отображения.

    :param chat_id: Ид чата.
    :return: Готовое сообщение для отправки.
    """
    current_date = datetime.now()
    formatted_date = f"{current_date.strftime("%d.%m.%Y").upper()} {days_of_the_week[current_date.weekday()]}"

    user: User = await get_user_with_group_and_schedule_by_chat_id(
        chat_id=chat_id, session=session
    )
    today_schedule = [
        schedule for schedule in user.group.schedule if schedule.date == formatted_date
    ]

    done_schedule = formatter_schedule(today_schedule)
    if done_schedule:
        return done_schedule
    else:
        return "Сегодня занятий нет! 🎉"


async def get_tomorrow_schedule(session: AsyncSession, chat_id: int) -> str:
    """
    Формирует расписание на завтрашний день для пользователя.

    Функция извлекает завтрашнюю дату и на основе её формата ищет
    занятия пользователя на следующий день. Возвращает строку с
    отформатированным расписанием для отображения.

    :param chat_id: Ид чата.
    :return: Готовое сообщение для отправки.
    """
    tomorrow_date = datetime.now() + timedelta(days=1)
    formatted_date = f"{tomorrow_date.strftime("%d.%m.%Y").upper()} {days_of_the_week[tomorrow_date.weekday()]}"

    user: User = await get_user_with_group_and_schedule_by_chat_id(
        chat_id=chat_id, session=session
    )
    tomorrow_schedule = [
        schedule for schedule in user.group.schedule if schedule.date == formatted_date
    ]

    done_schedule = formatter_schedule(tomorrow_schedule)
    if done_schedule:
        return done_schedule
    else:
        return "Завтра занятий нет! 🎊"


async def get_weekly_schedule(session: AsyncSession, chat_id: int) -> str:
    """
    Формирует расписание на неделю для пользователя.

    Функция извлекает все занятия пользователя и возвращает
    их в отформатированном виде для отображения. Расписание
    включает все доступные занятия пользователя на текущую неделю.

    :param chat_id: Ид чата.
    :return: Готовое сообщение для отправки.
    """
    user: User = await get_user_with_group_and_schedule_by_chat_id(
        chat_id=chat_id, session=session
    )

    done_schedule = formatter_schedule(user.group.schedule)
    if done_schedule:
        return done_schedule
    else:
        return "На этой неделе занятий нет! 🥳"
