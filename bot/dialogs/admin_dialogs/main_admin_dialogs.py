from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Format, Const

from bot.states import AdminStates
from bot.utils.admin_utils.admin_getters import get_admin_stats
from bot.utils.admin_utils.admin_sender import make_sender


GoToAdminMenu = SwitchTo(
    Const("← В админ меню"),
    state=AdminStates.main_menu,
    id="go_to_admin_menu",
)


main_menu_admin_window = Window(
    Format("{text}"),
    SwitchTo(
        Const("📢 Сделать рассылку"),
        state=AdminStates.sender,
        id="make_send",
    ),
    state=AdminStates.main_menu,
    getter=get_admin_stats,
)


make_sending_window = Window(
    Const("✏️ Введите сообщение, которое будет отправлено всем пользователям."),
    MessageInput(make_sender),
    GoToAdminMenu,
    state=AdminStates.sender,
)
