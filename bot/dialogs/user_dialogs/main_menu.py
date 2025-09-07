from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import SwitchTo, Row
from aiogram_dialog.widgets.text import Const

from bot.states import UserStates
from bot.utils.user_utils.utils import GoToMainMenuButton


main_menu_student = Window(
    Const("🎓 <b>Главное меню</b>\n\n" "Выберите действие:"),
    SwitchTo(
        Const("📌 На сегодня"),
        state=UserStates.schedule_today,
        id="schedule_for_today",
    ),
    Row(
        SwitchTo(
            Const("🌅 На завтра"),
            state=UserStates.schedule_tomorrow,
            id="schedule_for_tomorrow",
        ),
        SwitchTo(
            Const("📆 На неделю"),
            state=UserStates.schedule_week,
            id="schedule_for_week",
        ),
    ),
    SwitchTo(
        Const("➡️ Другие расписания"),
        state=UserStates.other_scheduler,
        id="other_scheduler_menu",
    ),
    Row(
        SwitchTo(
            Const("🔄 Сменить группу"),
            id="reconfigure_student_profile",
            state=UserStates.status,
        ),
        SwitchTo(
            Const("🔔 Уведомления"),
            id="notifications_settings_open",
            state=UserStates.notifications_settings,
        ),
    ),
    SwitchTo(
        Const("💸 Поддержать бота"),
        id="donate",
        state=UserStates.donate,
    ),
    state=UserStates.main_menu_student,
)


other_scheduler_window = Window(
    Const("Другие расписания"),
    SwitchTo(
        Const("👥 Расписание группы"),
        id="other_groups_eduform",
        state=UserStates.other_groups_form,
    ),
    Row(
        SwitchTo(
            Const("🏫 Аудитории"),
            id="check_schedule_rooms",
            state=UserStates.rooms_list,
        ),
        SwitchTo(
            Const("👨‍🏫 Преподаватели"),
            id="check_schedule_teachers",
            state=UserStates.prepod_list,
        ),
    ),
    GoToMainMenuButton,
    state=UserStates.other_scheduler,
)


main_menu_teacher = Window(
    Const("👨‍🏫 <b>Главное меню</b>\n\nВыберите действие:"),
    SwitchTo(
        Const("📌 На сегодня"),
        state=UserStates.schedule_today,
        id="schedule_for_today",
    ),
    Row(
        SwitchTo(
            Const("🌅 На завтра"),
            state=UserStates.schedule_tomorrow,
            id="schedule_for_tomorrow",
        ),
        SwitchTo(
            Const("📆 На неделю"),
            state=UserStates.schedule_week,
            id="schedule_for_week",
        ),
    ),
    SwitchTo(
        Const("➡️ Другие расписания"),
        state=UserStates.other_scheduler,
        id="other_scheduler_menu",
    ),
    SwitchTo(
        Const("🔔 Уведомления"),
        id="notifications_settings_open",
        state=UserStates.notifications_settings,
    ),
    SwitchTo(
        Const("🔄 Пройти регистрацию заново"),
        id="set_status_prepod",
        state=UserStates.status,
    ),
    SwitchTo(
        Const("💸 Поддержать бота"),
        id="donate",
        state=UserStates.donate,
    ),
    state=UserStates.main_menu_teacher,
)
