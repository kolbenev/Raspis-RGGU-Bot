from aiogram_dialog import Dialog

from bot.dialogs.admin_dialogs.main_admin_dialogs import (
    make_sending_window,
    main_menu_admin_window,
)

dialog = Dialog(
    main_menu_admin_window,
    make_sending_window,
)
