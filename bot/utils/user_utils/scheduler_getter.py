from datetime import datetime, timedelta, timezone, date
from typing import Any, Dict, List

from aiogram_dialog import DialogManager

from config.logger import logger
from database.utils import get_user_by_user_id
from database.confdb import session
from database.models import User
from api.rsuh_api import RgguScheduleClient


MOSCOW_TZ = timezone(timedelta(hours=3))
PAIR_TIME_MAP: Dict[int, str] = {
    1: "08.30 - 09.50",
    2: "10.15 - 11.35",
    3: "12.10 - 13.30",
    4: "13.40 - 15.00",
    5: "15.10 - 16.30",
    6: "16.40 - 18.00",
    7: "18.10 - 19.30",
    8: "19.40 - 21.00",
}


def parse_tbl_date_to_iso(date_text_with_weekday: str) -> str | None:
    """
    Преобразовать дату в формате 'дд.мм.гггг' в ISO-строку.
    """
    if not date_text_with_weekday:
        return None
    try:
        only_date = date_text_with_weekday.split()[0]
        d = datetime.strptime(only_date, "%d.%m.%Y").date()
        return d.isoformat()
    except Exception:
        return None


def iter_tbl_days(schedule_payload: Any) -> List[Dict[str, Any]]:
    """
    Вернуть список дней из payload расписания.
    """
    if isinstance(schedule_payload, dict) and isinstance(
        schedule_payload.get("tblData"), list
    ):
        return [day for day in schedule_payload["tblData"] if isinstance(day, dict)]
    return []


def filter_tbl_days_between(
    schedule_payload: Any, start_date_obj: date, end_date_obj: date
) -> List[Dict[str, Any]]:
    """
    Отфильтровать дни
    расписания по диапазону дат.
    """
    days = iter_tbl_days(schedule_payload)
    result: List[Dict[str, Any]] = []
    for day in days:
        header_date_text = str(day.get("date") or "")
        iso = parse_tbl_date_to_iso(header_date_text)
        if not iso:
            continue
        current = datetime.fromisoformat(iso).date()
        if start_date_obj <= current <= end_date_obj:
            result.append(day)
    return result


def format_day_block(day_obj: Dict[str, Any]) -> str:
    """
    Сформировать текстовый
    блок расписания для одного дня.
    """
    header_date_text: str = str(day_obj.get("date") or "").strip()
    pairs: List[Dict[str, Any]] = day_obj.get("pairs") or []

    lines: List[str] = [f"<b>{header_date_text}:</b>"]

    def _pair_key(pair: Dict[str, Any]) -> int:
        try:
            return int(pair.get("pair") or 0)
        except Exception:
            return 0

    for pair in sorted(pairs, key=_pair_key):
        pair_number = pair.get("pair")
        time_range = (
            PAIR_TIME_MAP.get(int(pair_number)) if str(pair_number).isdigit() else None
        )

        if str(pair_number).isdigit():
            num = int(pair_number)
            lines.append(
                f"<u>{num}-я пара ({time_range}):</u>"
                if time_range
                else f"<u>{num}-я пара:</u>"
            )
        else:
            lines.append("<u>Пара:</u>")

        for flow in pair.get("flows") or []:
            subject_text = (flow.get("subject") or "Предмет").strip()
            lessontype_text = (flow.get("lessontype") or "").strip()
            teacher_text = (flow.get("teacher") or "").strip()
            room_text = (flow.get("room") or "").strip()

            if lessontype_text:
                lines.append(
                    f"{subject_text} ({lessontype_text})"
                    + (f" - ауд: {room_text}" if room_text else "")
                )
            else:
                lines.append(
                    subject_text + (f" - ауд: {room_text}" if room_text else "")
                )

            if teacher_text:
                lines.append(f"Преподаватель: {teacher_text}")

            lines.append("")

    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


async def fetch_schedule_payload_for_user(user_row: User) -> Any:
    """
    Получить payload расписания
    для конкретного пользователя
    (студента или преподавателя).
    """
    async with RgguScheduleClient() as api_client:
        if user_row.status == "teacher" and user_row.teacher_id:
            return await api_client.get_schedule_by_teacher(
                teacher_id=str(user_row.teacher_id)
            )
        if (
            user_row.status == "student"
            and user_row.eduform
            and user_row.course
            and user_row.group_id
        ):
            return await api_client.get_schedule_by_group(
                eduform=str(user_row.eduform),
                course=str(user_row.course),
                group_id=str(user_row.group_id),
            )
    return None


async def schedule_today_getter(
    dialog_manager: DialogManager, **kwargs
) -> Dict[str, Any]:
    """
    Вернуть расписание пользователя на сегодня.
    """
    user_tg = dialog_manager.event.from_user
    logger.debug(f"{user_tg.username}:{user_tg.id} запросил расписание: на сегодня")
    try:
        user = await get_user_by_user_id(
            user_id=user_tg.id,
            session=session,
        )
        if user is None:
            logger.warning(
                f"{user_tg.username}:{user_tg.id} не найден в БД при запросе 'на сегодня'"
            )
            return {
                "schedule_text": "Пользователь не найден. Пройдите регистрацию ещё раз."
            }

        schedule_payload = await fetch_schedule_payload_for_user(user)
        if not schedule_payload:
            logger.warning(
                f"{user_tg.username}:{user_tg.id} пустой payload расписания (today)"
            )
            return {
                "schedule_text": "Не удалось получить расписание. Проверьте профиль."
            }

        target = datetime.now(MOSCOW_TZ).date()
        days = filter_tbl_days_between(schedule_payload, target, target)
        logger.debug(
            f"{user_tg.username}:{user_tg.id} найдено дней на сегодня: {len(days)}"
        )
        if not days:
            return {"schedule_text": f"{target.strftime('%d.%m.%Y')} - Нет занятий. 🎉"}

        text = format_day_block(days[0])
        logger.info(f"{user_tg.username}:{user_tg.id} выдано расписание на сегодня")
        return {"schedule_text": text}

    except Exception as e:
        logger.exception(
            f"{user_tg.username}:{user_tg.id} ошибка при получении расписания на сегодня: {e!r}"
        )
        return {
            "schedule_text": "⚠️ Произошла неизвестная ошибка.\nПожалуйста, попробуйте позже 🙏"
        }


async def schedule_tomorrow_getter(
    dialog_manager: DialogManager, **kwargs
) -> Dict[str, Any]:
    """
    Вернуть расписание пользователя на завтра.
    """
    user_tg = dialog_manager.event.from_user
    logger.debug(f"{user_tg.username}:{user_tg.id} запросил расписание: на завтра")
    try:
        user = await get_user_by_user_id(
            user_id=user_tg.id,
            session=session,
        )
        if user is None:
            logger.warning(
                f"{user_tg.username}:{user_tg.id} не найден в БД при запросе 'на завтра'"
            )
            return {
                "schedule_text": "Пользователь не найден. Пройдите регистрацию ещё раз."
            }

        schedule_payload = await fetch_schedule_payload_for_user(user)
        if not schedule_payload:
            logger.warning(
                f"{user_tg.username}:{user_tg.id} пустой payload расписания (tomorrow)"
            )
            return {
                "schedule_text": "Не удалось получить расписание. Проверьте профиль."
            }

        target = (datetime.now(MOSCOW_TZ) + timedelta(days=1)).date()
        days = filter_tbl_days_between(schedule_payload, target, target)
        logger.debug(
            f"{user_tg.username}:{user_tg.id} найдено дней на завтра: {len(days)}"
        )
        if not days:
            return {"schedule_text": f"{target.strftime('%d.%m.%Y')} - Нет занятий. 🎉"}

        text = format_day_block(days[0])
        logger.info(f"{user_tg.username}:{user_tg.id} выдано расписание на завтра")
        return {"schedule_text": text}

    except Exception as e:
        logger.exception(
            f"{user_tg.username}:{user_tg.id} ошибка при получении расписания на завтра: {e!r}"
        )
        return {
            "schedule_text": "⚠️ Произошла неизвестная ошибка.\nПожалуйста, попробуйте позже 🙏"
        }


async def schedule_week_getter(
    dialog_manager: DialogManager, **kwargs
) -> Dict[str, Any]:
    """
    Вернуть расписание пользователя на неделю.
    """
    user_tg = dialog_manager.event.from_user
    logger.debug(f"{user_tg.username}:{user_tg.id} запросил расписание: на неделю")
    try:
        user = await get_user_by_user_id(
            user_id=user_tg.id,
            session=session,
        )
        if user is None:
            logger.warning(
                f"{user_tg.username}:{user_tg.id} не найден в БД при запросе 'на неделю'"
            )
            return {
                "schedule_text": "Пользователь не найден. Пройдите регистрацию ещё раз."
            }

        schedule_payload = await fetch_schedule_payload_for_user(user)
        if not schedule_payload:
            logger.warning(
                f"{user_tg.username}:{user_tg.id} пустой payload расписания (week)"
            )
            return {
                "schedule_text": "Не удалось получить расписание. Проверьте профиль."
            }

        start = datetime.now(MOSCOW_TZ).date()
        end = start + timedelta(days=6)

        days = filter_tbl_days_between(schedule_payload, start, end)
        logger.debug(
            f"{user_tg.username}:{user_tg.id} найдено дней за неделю: {len(days)}"
        )
        if not days:
            return {
                "schedule_text": f"📆 Расписание на неделю\n{start.strftime('%d.%m.%Y')}-{end.strftime('%d.%m.%Y')}\n\nНет занятий. 🎉"
            }

        day_blocks = [format_day_block(day) for day in days]
        schedule_text = (
            f"📆 Расписание на неделю\n{start.strftime('%d.%m.%Y')}-{end.strftime('%d.%m.%Y')}"
            + "\n\n"
            + "\n\n—\n\n".join(day_blocks)
        )

        logger.info(
            f"{user_tg.username}:{user_tg.id} выдано расписание на неделю ({len(days)} дней)"
        )
        return {"schedule_text": schedule_text}

    except Exception as e:
        logger.exception(
            f"{user_tg.username}:{user_tg.id} ошибка при получении расписания на неделю: {e!r}"
        )
        return {
            "schedule_text": "⚠️ Произошла неизвестная ошибка.\nПожалуйста, попробуйте позже 🙏"
        }
