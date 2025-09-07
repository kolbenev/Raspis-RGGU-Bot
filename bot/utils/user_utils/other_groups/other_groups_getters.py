from typing import Dict, Any, List
from aiogram_dialog import DialogManager
from api.rsuh_api import RgguScheduleClient


async def other_groups_eduforms_getter(
    dialog_manager: DialogManager, **kwargs
) -> Dict[str, Any]:
    """
    Получить список форм
    обучения для других групп из API.
    """
    async with RgguScheduleClient() as api:
        payload = await api.get_eduforms_courses()

    eduform_items = payload.get("eduform") or []
    eduforms = []
    for eduform_item in eduform_items:
        if not eduform_item or "id" not in eduform_item:
            continue
        title = (
            eduform_item.get("data")
            or eduform_item.get("description")
            or eduform_item["id"]
        )
        eduforms.append({"code": str(eduform_item["id"]), "title": str(title)})
    return {"eduforms": eduforms}


async def other_groups_courses_getter(
    dialog_manager: DialogManager, **kwargs
) -> Dict[str, Any]:
    """
    Вернуть список
    доступных курсов для других групп.
    """
    return {"courses": ["1", "2", "3", "4", "5", "6"]}


async def other_groups_list_getter(
    dialog_manager: DialogManager, **kwargs
) -> Dict[str, Any]:
    """
    Получить список групп
    по выбранной форме обучения и курсу.
    """
    dialog_data = dialog_manager.dialog_data
    eduform_code = str(dialog_data.get("other_eduform_code") or "")
    course_number = str(dialog_data.get("other_course") or "")
    if not (eduform_code and course_number):
        return {"groups": []}

    async with RgguScheduleClient() as api:
        groups_raw_list = await api.get_groups_list(
            eduform=eduform_code, course=course_number
        )

    groups: List[Dict[str, str]] = []
    if isinstance(groups_raw_list, list):
        for group_item in groups_raw_list:
            group_id = group_item.get("id")
            if not group_id:
                continue
            title = (
                group_item.get("data")
                or " — ".join(
                    part
                    for part in [
                        str(group_item.get("direction") or "").strip(),
                        str(group_item.get("profile") or "").strip(),
                    ]
                    if part
                )
                or str(group_id)
            )
            groups.append({"id": str(group_id), "title": str(title)})
    return {"groups": groups}
