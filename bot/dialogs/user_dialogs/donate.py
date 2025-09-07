from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.text import Const

from bot.handlers.payments_handler import donate_handler
from bot.states import UserStates
from bot.utils.user_utils.utils import GoToMainMenuButton


donate_window = Window(
    Const(
        "💸 <b>Поддержать бота</b>\n\n"
        "Выберите количество звёзд ⭐️, "
        "которыми вы хотите поддержать проект:"
    ),
    Row(
        Button(
            Const("⭐️ 25"),
            id="donate_1",
            on_click=donate_handler
        ),
        Button(
            Const("⭐️ 50"),
            id="donate_50",
            on_click=donate_handler
        ),
    ),
    Row(
        Button(
            Const("⭐ 100"),
            id="donate_100",
            on_click=donate_handler
        ),
        Button(
            Const("⭐ 200"),
            id="donate_200",
            on_click=donate_handler
        ),
    ),
    GoToMainMenuButton,
    state=UserStates.donate,
)
