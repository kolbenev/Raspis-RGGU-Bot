from typing import Dict, Any, List
from aiogram_dialog import DialogManager
from api.rsuh_api import RgguScheduleClient
from config.logger import logger


async def rooms_list_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Получить список аудиторий из
    API РГГУ и вернуть в формате для диалога.
    """
    from_user = dialog_manager.event.from_user
    logger.debug(f"{from_user.username}:{from_user.id} запросил список аудиторий")

    try:
        async with RgguScheduleClient() as api:
            rooms_raw = await api.get_rooms_list()

        rooms: List[Dict[str, str]] = []
        if isinstance(rooms_raw, list):
            for room_raw in rooms_raw:
                if not isinstance(room_raw, dict) or not room_raw.get("id"):
                    continue
                rooms.append(
                    {
                        "id": str(room_raw.get("id")),
                        "name": str(room_raw.get("data", "")).strip(),
                    }
                )

        logger.debug(
            f"{from_user.username}:{from_user.id} получено аудиторий: {len(rooms)}"
        )
        return {"rooms": rooms}

    except Exception as e:
        logger.exception(
            f"{from_user.username}:{from_user.id} ошибка при получении аудиторий: {e!r}"
        )
        return {"rooms": []}
