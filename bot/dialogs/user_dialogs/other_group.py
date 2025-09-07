from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Back, ScrollingGroup, Select
from bot.states import UserStates
from bot.utils.user_utils.other_groups.other_groups_getters import (
    other_groups_eduforms_getter,
    other_groups_courses_getter,
    other_groups_list_getter,
)
from bot.utils.user_utils.other_groups.other_groups_handlers import (
    on_other_group_eduform_chosen,
    on_other_group_course_chosen,
    on_other_group_chosen_show_schedule,
)
from bot.utils.user_utils.utils import GoToMainMenuButton


other_groups_eduform_select_window = Window(
    Const("🏫 Выберите форму обучения:"),
    ScrollingGroup(
        Select(
            Format("{item[title]}"),
            id="other_eduform_item",
            item_id_getter=lambda item: str(item["code"]),
            items="eduforms",
            on_click=on_other_group_eduform_chosen,
        ),
        id="other_eduforms_scroll",
        width=1,
        height=6,
    ),
    GoToMainMenuButton,
    getter=other_groups_eduforms_getter,
    state=UserStates.other_groups_form,
)

other_groups_course_select_window = Window(
    Const("🎓 Выберите курс:"),
    Select(
        Format("{item}"),
        id="other_course_item",
        item_id_getter=lambda item: str(item),
        items="courses",
        on_click=on_other_group_course_chosen,
    ),
    Back(Const("← Назад")),
    getter=other_groups_courses_getter,
    state=UserStates.other_groups_course,
)

other_groups_group_select_window = Window(
    Const("👥 Выберите группу:\nЛистайте список стрелками."),
    ScrollingGroup(
        Select(
            Format("{item[title]}"),
            id="other_group_item",
            item_id_getter=lambda item: str(item["id"]),
            items="groups",
            on_click=on_other_group_chosen_show_schedule,
        ),
        id="other_groups_scroll",
        width=1,
        height=10,
    ),
    Back(Const("← Назад")),
    getter=other_groups_list_getter,
    state=UserStates.other_groups_list,
)
