from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import (
    ScrollingGroup,
    Select,
    Button,
)
from bot.states import UserStates
from bot.utils.user_utils.notifications.notifications_getters import (
    notifications_times_getter,
)
from bot.utils.user_utils.notifications.notifications_handlers import (
    on_notify_time_chosen,
    on_notifications_disable,
)
from bot.utils.user_utils.utils import GoToMainMenuButton


notifications_settings_window = Window(
    Format(
        "🔔 Выберите время, в которое вы будете получать расписание на завтра.\n"
        "{current_setting}"
    ),
    ScrollingGroup(
        Select(
            Format("{item[title]}"),
            id="notify_time_item",
            item_id_getter=lambda item: item["id"],
            items="times",
            on_click=on_notify_time_chosen,
        ),
        id="notify_times_scroll",
        width=3,
        height=7,
    ),
    Button(
        Const("🚫 Отключить"),
        id="disable_notifications_button",
        on_click=on_notifications_disable,
    ),
    GoToMainMenuButton,
    getter=notifications_times_getter,
    state=UserStates.notifications_settings,
)
