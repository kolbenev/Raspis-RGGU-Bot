from datetime import datetime, timedelta
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select

from bot.utils.user_utils.utils import send_correct_menu
from config.logger import logger
from database.confdb import session
from database.utils import get_user_by_user_id
from api.rsuh_api import RgguScheduleClient
from bot.states import UserStates
from bot.utils.user_utils.scheduler_getter import (
    MOSCOW_TZ,
    filter_tbl_days_between,
    format_day_block,
)


SEPARATOR_BETWEEN_DAYS = "—"


async def on_other_group_eduform_chosen(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """
    Сохранить выбранную форму
    обучения и переключить на выбор курса.
    """
    from_user = callback.from_user
    logger.debug(
        f"{from_user.username}:{from_user.id} other-groups выбрал форму: {item_id}"
    )
    dialog_manager.dialog_data["other_eduform_code"] = str(item_id)
    await dialog_manager.switch_to(UserStates.other_groups_course)


async def on_other_group_course_chosen(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """
    Сохранить выбранный курс
    и переключить на выбор группы.
    """
    from_user = callback.from_user
    logger.debug(
        f"{from_user.username}:{from_user.id} other-groups выбрал курс: {item_id}"
    )
    dialog_manager.dialog_data["other_course"] = str(item_id)
    await dialog_manager.switch_to(UserStates.other_groups_list)


async def on_other_group_chosen_show_schedule(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """
    Показать расписание выбранной
     группы на неделю и вернуть меню пользователю.
    """
    from_user = callback.from_user
    logger.debug(
        f"{from_user.username}:{from_user.id} other-groups выбрал группу: {item_id}"
    )

    eduform_code = str(dialog_manager.dialog_data.get("other_eduform_code") or "")
    course_number = str(dialog_manager.dialog_data.get("other_course") or "")
    if not (eduform_code and course_number):
        await callback.answer("Сначала выберите форму и курс.", show_alert=True)
        return

    try:
        async with RgguScheduleClient() as api:
            payload = await api.get_schedule_by_group(
                eduform=eduform_code, course=course_number, group_id=str(item_id)
            )

        start_date = datetime.now(MOSCOW_TZ).date()
        end_date = start_date + timedelta(days=6)
        days = filter_tbl_days_between(payload, start_date, end_date)

        user = await get_user_by_user_id(
            user_id=from_user.id,
            session=session,
        )

        if not days:
            await callback.message.answer(
                f"📆 Расписание на неделю\n{start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')}\n\nНет занятий. 🎉"
            )
            await send_correct_menu(
                user=user,
                dialog_manager=dialog_manager,
            )
            return

        blocks = [format_day_block(day) for day in days]
        text = (
            f"📆 Расписание на неделю\n{start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')}"
            + "\n\n"
            + f"\n\n{SEPARATOR_BETWEEN_DAYS}\n\n".join(blocks)
        )
        await callback.message.answer(text)

        await send_correct_menu(
            user=user,
            dialog_manager=dialog_manager,
        )

    except Exception as e:
        logger.exception(
            f"{from_user.username}:{from_user.id} ошибка показа расписания группы {item_id}: {e!r}"
        )
        await callback.message.answer(
            "⚠️ Произошла неизвестная ошибка.\nПожалуйста, попробуйте позже 🙏"
        )
