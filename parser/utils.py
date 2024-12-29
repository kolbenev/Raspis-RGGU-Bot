from datetime import datetime, timedelta
from typing import Dict, List

import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy import select

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
    Запрашивает HTML-страницу и извлекает таблицу с
    расписанием из её кода и возвращает её содержимое
    в виде списка списков строк.

    :param url: URL-адрес для запроса.
    :param params: Параметры для post запроса.
    :return: Расписание в формате списка.
    """
    async with aiohttp.ClientSession() as client:
        try:
            async with client.post(url=url, data=params) as response:
                response.raise_for_status()
                html = await response.text()
        except aiohttp.ClientError as e:
            logger.error(e)
            raise ValueError(f"Ошибка при запросе: {e}")

    soup = BeautifulSoup(html, "html.parser")
    schedule = [
        [cell.get_text(strip=True) for cell in row.find_all("td")]
        for row in soup.find_all("tr")
        if row.find_all("td")
    ]

    if not schedule:
        logger.error(f"get_schedule не получил расписание для {params["kyrs"]}|{params["formob"]}|{params["caf"]}")

    return schedule
