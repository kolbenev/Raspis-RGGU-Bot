from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const

from bot.states import UserStates
from bot.utils.user_utils.scheduler_getter import (
    schedule_today_getter,
    schedule_tomorrow_getter,
    schedule_week_getter,
)
from bot.utils.user_utils.utils import go_to_back_menu_from_scheduler


GoToMenuForScheduler = Button(
    Const("← В меню"),
    on_click=go_to_back_menu_from_scheduler,
    id="go_to_back_menu_from_scheduler",
)


schedule_today_window = Window(
    Format("{schedule_text}"),
    GoToMenuForScheduler,
    getter=schedule_today_getter,
    state=UserStates.schedule_today,
)


schedule_tomorrow_window = Window(
    Format("{schedule_text}"),
    GoToMenuForScheduler,
    getter=schedule_tomorrow_getter,
    state=UserStates.schedule_tomorrow,
)


schedule_week_window = Window(
    Format("{schedule_text}"),
    GoToMenuForScheduler,
    getter=schedule_week_getter,
    state=UserStates.schedule_week,
)
