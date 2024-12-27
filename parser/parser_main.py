"""
Основной модуль парсера.
"""

from database.models import Schedule
from database.confdb import session
from parser.config import url, pars_time
from parser.utils import maker_params, get_schedule, get_group
from bot.utils.other.logger import logger


async def parsing_schedule(formob, kyrs, caf):
    """
    Функция для парсинга расписания с удаленного
    источника и сохранения его в базу данных.

    Она использует параметры формы обучения, курса и кафедры для получения расписания
    с помощью функции `get_schedule` и данных о группе с помощью функции `get_group`.
    Затем парсит расписание, создает объекты `Schedule` и сохраняет их в базу данных.

    :param formob: Форма обучения.
    :param kyrs: Курс.
    :param caf: ID Кафедры.
    """
    params = maker_params(formob, kyrs, caf)
    schedule = await get_schedule(url=url, params=params)
    group = await get_group(caf=caf)
    logger.info(f"Запущен парсинг расписания для {group.name}")

    current_date = ""
    current_para = ""

    schedule_list = []
    for line in schedule[1:]:
        if len(line) == 8:
            current_date = line[0]
            current_para = line[1]
        elif len(line) == 7:
            current_para = line[0]

        new_schedule = Schedule(
            group_id=group.id,
            date=current_date,
            para=current_para,
            lecture_time=pars_time[current_para],
            audience=line[-4],
            lesson=line[-3],
            type_lesson=line[-2],
            teacher_name=line[-1],
        )
        schedule_list.append(new_schedule)
    else:
        session.add_all(schedule_list)
        await session.commit()
