from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from bot.states import UserStates
from database.confdb import session
from database.models import User
from database.utils import get_user_by_user_id


async def send_correct_menu(
    dialog_manager: DialogManager,
    user: User,
):
    """
    Перенаправляет пользователя в
    верное меню.
    """
    if user.status == "student":
        await dialog_manager.switch_to(
            state=UserStates.main_menu_student,
            show_mode=ShowMode.DELETE_AND_SEND,
        )
    elif user.status == "teacher":
        await dialog_manager.switch_to(
            state=UserStates.main_menu_teacher, show_mode=ShowMode.DELETE_AND_SEND
        )


async def go_to_back_menu(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    user = await get_user_by_user_id(
        user_id=callback.from_user.id,
        session=session,
    )

    if user is None:
        return

    await send_correct_menu(
        user=user,
        dialog_manager=dialog_manager,
    )


async def go_to_back_menu_from_scheduler(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    user = await get_user_by_user_id(
        user_id=callback.from_user.id,
        session=session,
    )

    if user is None:
        return

    target_state = (
        UserStates.status
        if not user
        else (
            UserStates.main_menu_student
            if user.status == "student"
            else UserStates.main_menu_teacher
        )
    )

    await dialog_manager.switch_to(
        state=target_state,
        show_mode=ShowMode.SEND,
    )


GoToMainMenuButton = Button(
    Const("← В меню"),
    on_click=go_to_back_menu,
    id="go_to_back_menu",
)
