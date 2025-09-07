from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import (
    Row,
    SwitchTo,
    Back,
    Select,
    ScrollingGroup,
)

from bot.states import UserStates
from bot.utils.user_utils.registration.registration_getters import (
    teacher_select_getter,
    student_course_getter,
    student_eduform_getter,
    student_directions_getter,
)
from bot.utils.user_utils.registration.registration_handlers import (
    on_teacher_chosen,
    on_direction_chosen,
    on_course_chosen,
    on_eduform_chosen,
)


status_select_window = Window(
    Const("👋 Привет! Давайте познакомимся\nКто вы?"),
    Row(
        SwitchTo(
            Const("🎓 Студент"),
            id="to_student",
            state=UserStates.student_course,
        ),
        SwitchTo(
            Const("👨‍🏫 Преподаватель"),
            id="to_teacher",
            state=UserStates.teacher_select,
        ),
    ),
    state=UserStates.status,
)

teacher_select_window = Window(
    Const(
        "👨‍🏫 Выберите себя из списка преподавателей:\nЛистайте список с помощью стрелок."
    ),
    ScrollingGroup(
        Select(
            Format("{item[name]}"),
            id="teacher_item",
            item_id_getter=lambda item: str(item["id"]),
            items="teachers",
            on_click=on_teacher_chosen,
        ),
        id="teachers_scroll",
        width=1,
        height=20,
    ),
    getter=teacher_select_getter,
    state=UserStates.teacher_select,
)

student_course_select_window = Window(
    Const("🎓 Выберите курс:"),
    Select(
        Format("{item}"),
        id="course_item",
        item_id_getter=lambda item: str(item),
        items="courses",
        on_click=on_course_chosen,
    ),
    getter=student_course_getter,
    state=UserStates.student_course,
)

student_eduform_select_window = Window(
    Const("🏫 Выберите форму обучения:"),
    ScrollingGroup(
        Select(
            Format("{item[title]}"),
            id="eduform_item",
            item_id_getter=lambda item: str(item["code"]),
            items="eduforms",
            on_click=on_eduform_chosen,
        ),
        id="eduforms_scroll",
        width=1,
        height=5,
    ),
    Back(Const("← Назад")),
    getter=student_eduform_getter,
    state=UserStates.student_form,
)

student_direction_select_window = Window(
    Const("📚 Выберите направление подготовки:"),
    ScrollingGroup(
        Select(
            Format("{item[title]}"),
            id="direction_item",
            item_id_getter=lambda item: str(item["id"]),
            items="directions",
            on_click=on_direction_chosen,
        ),
        id="directions_scroll",
        width=1,
        height=5,
    ),
    Back(Const("← Назад")),
    getter=student_directions_getter,
    state=UserStates.student_direction,
)
