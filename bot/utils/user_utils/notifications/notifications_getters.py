from typing import Dict, Any, List
from aiogram_dialog import DialogManager
from database.utils import get_user_by_user_id
from database.confdb import session


async def notifications_times_getter(
    dialog_manager: DialogManager, **kwargs
) -> Dict[str, Any]:
    """
    Сформировать список доступных
    времён для уведомлений и
    вернуть текущее состояние пользователя.
    """
    times: List[Dict[str, str]] = [
        {"id": f"{hour:02d}:{minute:02d}", "title": f"{hour:02d}:{minute:02d}"}
        for hour in range(24)
        for minute in range(0, 60, 5)
    ]

    user = await get_user_by_user_id(
        user_id=dialog_manager.event.from_user.id,
        session=session,
    )

    if user and user.notify_enabled and user.notify_time:
        current_setting = f"\nТекущая настройка: ✅ в {user.notify_time}"
    else:
        current_setting = "\nТекущая настройка: ❌ уведомления выключены"

    return {"times": times, "current_setting": current_setting}
