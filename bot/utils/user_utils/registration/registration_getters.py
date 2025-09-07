from typing import Dict, Any
from aiogram_dialog import DialogManager
from api.rsuh_api import RgguScheduleClient
from config.logger import logger


async def teacher_select_getter(
    dialog_manager: DialogManager, **kwargs
) -> Dict[str, Any]:
    """
    Получить список преподавателей
    из API и вернуть для выбора в диалоге.
    """
    try:
        async with RgguScheduleClient() as api:
            teachers_raw_list = await api.get_teachers_list()

        teachers_list = [
            {"id": str(teacher.get("id")), "name": str(teacher.get("data", ""))}
            for teacher in (
                teachers_raw_list if isinstance(teachers_raw_list, list) else []
            )
            if teacher.get("id")
        ]

        logger.debug(
            f"user:{dialog_manager.event.from_user.id} запросил список преподавателей, получено: {len(teachers_list)}"
        )
        return {"teachers": teachers_list}

    except Exception as e:
        logger.error(
            f"user:{dialog_manager.event.from_user.id} ошибка при получении списка преподавателей: {e}"
        )
        return {"teachers": []}


async def student_course_getter(
    dialog_manager: DialogManager, **kwargs
) -> Dict[str, Any]:
    """
    Вернуть список
    доступных курсов обучения.
    """
    courses_list = ["1", "2", "3", "4", "5", "6"]
    logger.debug(
        f"user:{dialog_manager.event.from_user.id} запросил список курсов, доступно: {courses_list}"
    )
    return {"courses": courses_list}


async def student_eduform_getter(
    dialog_manager: DialogManager, **kwargs
) -> Dict[str, Any]:
    """
    Получить список форм обучения
    из API и вернуть для выбора в диалоге.
    """
    try:
        async with RgguScheduleClient() as api:
            eduforms_payload = await api.get_eduforms_courses()

        eduform_items = eduforms_payload.get("eduform") or []
        eduforms_list = [
            {
                "code": str(eduform_item["id"]),
                "title": str(
                    eduform_item.get("data")
                    or eduform_item.get("description")
                    or eduform_item["id"]
                ),
            }
            for eduform_item in eduform_items
            if eduform_item and "id" in eduform_item
        ]

        logger.debug(
            f"user:{dialog_manager.event.from_user.id} запросил формы обучения, получено: {len(eduforms_list)}"
        )
        return {"eduforms": eduforms_list}

    except Exception as e:
        logger.error(
            f"user:{dialog_manager.event.from_user.id} ошибка при получении форм обучения: {e}"
        )
        return {"eduforms": []}


async def student_directions_getter(
    dialog_manager: DialogManager, **kwargs
) -> Dict[str, Any]:
    """
    Получить направления/группы
    для выбранных формы обучения и курса.
    """
    dialog_data = dialog_manager.dialog_data
    selected_eduform_code = str(dialog_data.get("eduform_code") or "")
    selected_course_number = str(dialog_data.get("course") or "")

    if not (selected_eduform_code and selected_course_number):
        logger.warning(
            f"user:{dialog_manager.event.from_user.id} не указал eduform/course, directions пустые"
        )
        return {"directions": []}

    try:
        async with RgguScheduleClient() as api:
            groups_raw_list = await api.get_groups_list(
                eduform=selected_eduform_code,
                course=selected_course_number,
            )

        directions_list = []
        if isinstance(groups_raw_list, list):
            for group_item in groups_raw_list:
                group_id = group_item.get("id")
                if not group_id:
                    continue
                group_title = (
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
                directions_list.append({"id": str(group_id), "title": str(group_title)})

        logger.debug(
            f"user:{dialog_manager.event.from_user.id} запросил направления для eduform={selected_eduform_code}, course={selected_course_number}, получено: {len(directions_list)}"
        )
        return {"directions": directions_list}

    except Exception as e:
        logger.error(
            f"user:{dialog_manager.event.from_user.id} ошибка при получении directions для eduform={selected_eduform_code}, course={selected_course_number}: {e}"
        )
        return {"directions": []}
