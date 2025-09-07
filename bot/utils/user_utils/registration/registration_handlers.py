import asyncio

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select
from sqlalchemy import select

from bot.states import UserStates
from config.logger import logger
from database.confdb import session
from database.models import User
from database.utils import create_new_user


async def on_course_chosen(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    from_user = callback.from_user
    logger.debug(f"{from_user.username}:{from_user.id} выбрал курс: {item_id}")
    dialog_manager.dialog_data["course"] = str(item_id)
    await dialog_manager.switch_to(UserStates.student_form)


async def on_eduform_chosen(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    from_user = callback.from_user
    logger.debug(
        f"{from_user.username}:{from_user.id} выбрал форму обучения: {item_id}"
    )
    dialog_manager.dialog_data["eduform_code"] = str(item_id)
    await dialog_manager.switch_to(UserStates.student_direction)


async def on_teacher_chosen(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    from_user = callback.from_user
    logger.debug(f"{from_user.username}:{from_user.id} выбрал преподавателя: {item_id}")

    result = await session.execute(select(User).where(User.user_id == from_user.id))
    user = result.scalars().first()

    if user is None:
        logger.info(f"Создание нового пользователя {from_user.id} как преподавателя")
        await create_new_user(
            chat_id=callback.message.chat.id,
            user_id=from_user.id,
            username=from_user.username,
            session=session,
            status="teacher",
            teacher_id=item_id[0],
        )

    else:
        logger.info(f"Обновление пользователя {from_user.id} -> статус teacher")
        user.status = "teacher"
        user.chat_id = callback.message.chat.id
        user.user_id = from_user.id
        user.username = from_user.username
        user.teacher_id = item_id
        user.course = None
        user.eduform = None
        user.group_id = None
        session.add(user)
        await session.commit()

    send_message = await dialog_manager.event.message.answer(
        text="✅ Вы успешно зарегистрировались в боте!",
    )

    await asyncio.sleep(2)

    try:
        await send_message.delete()
    except:
        pass

    await dialog_manager.switch_to(
        UserStates.main_menu_teacher, show_mode=ShowMode.DELETE_AND_SEND
    )


async def on_direction_chosen(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    from_user = callback.from_user
    course_value = str(dialog_manager.dialog_data.get("course") or "")
    eduform_code_value = str(dialog_manager.dialog_data.get("eduform_code") or "")
    group_id_value = str(item_id)

    logger.debug(
        f"{from_user.username}:{from_user.id} выбрал направление: {group_id_value}, "
        f"курс={course_value}, форма={eduform_code_value}"
    )

    if not (course_value and eduform_code_value and group_id_value):
        logger.warning(
            f"Пользователь {from_user.id} выбрал направление без всех параметров"
        )
        await callback.answer(
            "Не все параметры выбраны. Вернитесь назад и повторите.", show_alert=True
        )
        return

    result = await session.execute(select(User).where(User.user_id == from_user.id))
    user = result.scalars().first()

    if user is None:
        logger.info(f"Создание нового пользователя {from_user.id} как студента")
        await create_new_user(
            chat_id=callback.message.chat.id,
            user_id=from_user.id,
            username=from_user.username,
            session=session,
            status="student",
            course=course_value,
            eduform=eduform_code_value,
            group_id=group_id_value,
        )

    else:
        logger.info(f"Обновление пользователя {from_user.id} -> статус student")
        user.chat_id = callback.message.chat.id
        user.user_id = from_user.id
        user.username = from_user.username
        user.status = "student"
        user.course = course_value
        user.eduform = eduform_code_value
        user.group_id = group_id_value
        session.add(user)
        await session.commit()

    send_message = await dialog_manager.event.message.answer(
        text="✅ Вы успешно зарегистрировались в боте!",
    )

    await asyncio.sleep(2)

    try:
        await send_message.delete()
    except:
        pass
    await dialog_manager.switch_to(
        UserStates.main_menu_student, show_mode=ShowMode.DELETE_AND_SEND
    )
