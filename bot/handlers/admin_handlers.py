from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, ShowMode

from bot.states import AdminStates, UserStates
from database.confdb import session
from database.utils import get_user_by_user_id


router = Router()


@router.message(Command("admin"))
async def give_admin_menu(
    message: Message,
    dialog_manager: DialogManager,
):
    """
    Выдает административное меню.
    """
    user = await get_user_by_user_id(user_id=message.from_user.id, session=session)

    if user.is_admin:
        await dialog_manager.start(
            state=AdminStates.main_menu,
            mode=StartMode.RESET_STACK,
            show_mode=ShowMode.DELETE_AND_SEND,
        )
    else:
        target_state = (
            UserStates.status
            if not user
            else (
                UserStates.main_menu_student
                if user.status == "student"
                else UserStates.main_menu_teacher
            )
        )

        await dialog_manager.start(
            state=target_state,
            mode=StartMode.RESET_STACK,
            show_mode=ShowMode.SEND,
        )
