"""
Модуль утилит для парсера.
"""

from datetime import datetime, timedelta
from typing import Dict, List

import aiohttp
from sqlalchemy import select
from lxml import html

from bot.middlewares.logger import logger
from database.confdb import session
from database.models import Group


def maker_params(formob, kyrs, caf) -> Dict:
    """
    Фукнция для формирования параметров, для post
    запроса на получение расписания на неделю.

    :param formob: Форма обучения.
    :param kyrs: Курс.
    :param caf: ID Кафедры.
    :return: Словарь с параметрами для запросов.
    """
    date_today = datetime.today()
    date_in_a_week = datetime.today() + timedelta(weeks=1)
    params = {
        "formob": formob,
        "kyrs": kyrs,
        "srok": "interval",
        "caf": caf,
        "cafzn": "None",
        "sdate_year": str(date_today.year),
        "sdate_month": str(date_today.month),
        "sdate_day": str(date_today.day),
        "fdate_year": str(date_in_a_week.year),
        "fdate_month": str(date_in_a_week.month),
        "fdate_day": str(date_in_a_week.day),
    }
    return params


async def get_group(caf: str) -> Group:
    """
    Функция для получения модели группы
    по ID кафедры.

    :param caf: ID кафедры.
    :return: Модель группы.
    """
    stmt = select(Group).where(Group.caf == caf)
    result = await session.execute(stmt)
    group = result.scalars().first()
    return group


async def get_schedule(url: str, params: Dict) -> List[List[str]]:
    """
    Асинхронно извлекает таблицу расписания из HTML-страницы.

    :param url: URL-адрес для запроса.
    :param params: Параметры для POST-запроса.
    :return: Расписание в формате списка списков строк.
    """
    try:
        async with aiohttp.ClientSession() as client:
            async with client.post(url, data=params) as response:
                response.raise_for_status()
                html_content = await response.text()
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка при запросе: {e}")
        raise ValueError(f"Ошибка при запросе: {e}")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        raise ValueError(f"Непредвиденная ошибка: {e}")

    try:
        tree = html.fromstring(html_content)

        rows = tree.xpath("//tr[td]")
        schedule = [
            [td.text.strip() if td.text else "" for td in row.xpath("td")]
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Ошибка при парсинге HTML: {e}")
        raise ValueError(f"Ошибка при парсинге HTML: {e}")

    if not schedule:
        logger.error(
            f"Не удалось извлечь расписание для параметров: "
            f"{params.get('kyrs', 'не указано')}|"
            f"{params.get('formob', 'не указано')}|"
            f"{params.get('caf', 'не указано')}"
        )

    return schedule
