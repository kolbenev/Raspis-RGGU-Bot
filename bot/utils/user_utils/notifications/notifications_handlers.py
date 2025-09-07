from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select, Button

from bot.utils.user_utils.utils import send_correct_menu
from config.logger import logger
from database.confdb import session
from database.utils import get_user_by_user_id


def is_valid_hhmm(value: str) -> bool:
    """
    Проверить, что строка соответствует
    формату HH:MM с шагом 5 минут.
    """
    try:
        hours_str, minutes_str = value.split(":")
        hour, minute = int(hours_str), int(minutes_str)
        return 0 <= hour <= 23 and minute in {
            0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55,
        }
    except Exception:
        return False


async def on_notify_time_chosen(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """
    Обработать выбор времени
    уведомлений и сохранить настройку пользователю.
    """
    from_user = callback.from_user
    logger.debug(
        f"{from_user.username}:{from_user.id} выбрал время уведомлений: {item_id}"
    )

    if not is_valid_hhmm(item_id):
        await callback.answer("Неверный формат времени", show_alert=True)
        return

    user = await get_user_by_user_id(user_id=from_user.id, session=session)

    if user is None:
        await callback.answer("Сначала завершите регистрацию.", show_alert=True)
        return

    user.notify_time = item_id
    user.notify_enabled = True
    session.add(user)
    await session.commit()

    logger.info(
        f"{from_user.username}:{from_user.id} уведомления включены на {item_id}"
    )

    await callback.answer(f"Готово! Ежедневно в {item_id}", show_alert=False)

    await send_correct_menu(
        user=user,
        dialog_manager=dialog_manager,
    )


async def on_notifications_disable(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    """
    Обработать отключение
    уведомлений пользователем.
    """
    from_user = callback.from_user
    logger.debug(f"{from_user.username}:{from_user.id} отключает уведомления")

    user = await get_user_by_user_id(user_id=from_user.id, session=session)
    if user is None:
        await callback.answer("Сначала завершите регистрацию.", show_alert=True)
        return

    user.notify_enabled = False
    session.add(user)
    await session.commit()

    logger.info(f"{from_user.username}:{from_user.id} уведомления отключены")

    await callback.answer("Уведомления отключены", show_alert=False)
    await send_correct_menu(
        user=user,
        dialog_manager=dialog_manager,
    )
