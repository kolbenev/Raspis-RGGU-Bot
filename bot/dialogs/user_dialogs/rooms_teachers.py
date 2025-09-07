from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from bot.states import UserStates
from bot.utils.user_utils.registration.registration_getters import teacher_select_getter
from bot.utils.user_utils.rooms_prepod.getters_rooms import rooms_list_getter
from bot.utils.user_utils.rooms_prepod.handlers_rooms_teachers import (
    on_room_chosen_show_schedule,
    on_teacher_chosen_show_schedule,
)
from bot.utils.user_utils.utils import GoToMainMenuButton


rooms_list_window = Window(
    Const("🏫 Выберите аудиторию:\nЛистайте список стрелками."),
    ScrollingGroup(
        Select(
            Format("{item[name]}"),
            id="room_item",
            item_id_getter=lambda item: str(item["id"]),
            items="rooms",
            on_click=on_room_chosen_show_schedule,
        ),
        id="rooms_scroll",
        width=1,
        height=10,
    ),
    GoToMainMenuButton,
    getter=rooms_list_getter,
    state=UserStates.rooms_list,
)


teachers_schedule_select_window = Window(
    Const("👨‍🏫 Выберите преподавателя:\nЛистайте список стрелками."),
    ScrollingGroup(
        Select(
            Format("{item[name]}"),
            id="teacher_item_for_schedule",
            item_id_getter=lambda item: str(item["id"]),
            items="teachers",
            on_click=on_teacher_chosen_show_schedule,
        ),
        id="teachers_schedule_scroll",
        width=1,
        height=20,
    ),
    GoToMainMenuButton,
    getter=teacher_select_getter,
    state=UserStates.prepod_list,
)
