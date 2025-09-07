from datetime import datetime, timedelta
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select

from bot.utils.user_utils.utils import send_correct_menu
from database.confdb import session
from database.utils import get_user_by_user_id
from api.rsuh_api import RgguScheduleClient
from config.logger import logger

from bot.utils.user_utils.scheduler_getter import (
    MOSCOW_TZ,
    filter_tbl_days_between,
    format_day_block,
)


SEPARATOR_BETWEEN_DAYS = "—"


def format_week_text(payload, start_date, end_date) -> str:
    """
    Сформировать текст расписания
    на неделю из payload.
    """
    days = filter_tbl_days_between(payload, start_date, end_date)
    if not days:
        return (
            f"📆 Расписание на неделю\n"
            f"{start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')}\n\nНет занятий. 🎉"
        )

    blocks = [format_day_block(day) for day in days]
    header = (
        f"📆 Расписание на неделю\n"
        f"{start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')}"
    )
    return header + "\n\n" + f"\n\n{SEPARATOR_BETWEEN_DAYS}\n\n".join(blocks)


async def on_room_chosen_show_schedule(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """
    Показать расписание по выбранной
    аудитории и вернуть меню пользователю.
    """
    from_user = callback.from_user
    logger.debug(f"{from_user.username}:{from_user.id} выбрал аудиторию: {item_id}")

    try:
        async with RgguScheduleClient() as api:
            payload = await api.get_schedule_by_room(room_id=str(item_id))

        start_date = datetime.now(MOSCOW_TZ).date()
        end_date = start_date + timedelta(days=6)

        text = format_week_text(payload, start_date, end_date)
        await callback.message.answer(text)

        user = await get_user_by_user_id(
            user_id=from_user.id,
            session=session,
        )
        await send_correct_menu(
            user=user,
            dialog_manager=dialog_manager,
        )

    except Exception as e:
        logger.exception(
            f"{from_user.username}:{from_user.id} ошибка при показе расписания по аудитории {item_id}: {e!r}"
        )
        await callback.message.answer(
            "⚠️ Произошла неизвестная ошибка.\nПожалуйста, попробуйте позже 🙏"
        )


async def on_teacher_chosen_show_schedule(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """
    Показать расписание по выбранному
    преподавателю и вернуть меню пользователю.
    """
    from_user = callback.from_user
    logger.debug(
        f"{from_user.username}:{from_user.id} выбрал преподавателя (просмотр): {item_id}"
    )

    try:
        async with RgguScheduleClient() as api:
            payload = await api.get_schedule_by_teacher(teacher_id=str(item_id))

        start_date = datetime.now(MOSCOW_TZ).date()
        end_date = start_date + timedelta(days=6)

        text = format_week_text(payload, start_date, end_date)
        await callback.message.answer(text)

        user = await get_user_by_user_id(
            user_id=from_user.id,
            session=session,
        )
        await send_correct_menu(
            user=user,
            dialog_manager=dialog_manager,
        )

    except Exception as e:
        logger.exception(
            f"{from_user.username}:{from_user.id} ошибка при показе расписания по преподавателю {item_id}: {e!r}"
        )
        await callback.message.answer(
            "⚠️ Произошла неизвестная ошибка.\nПожалуйста, попробуйте позже 🙏"
        )
