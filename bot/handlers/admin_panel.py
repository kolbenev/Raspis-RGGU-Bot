"""
Модуль административной панели.
"""

from sqlalchemy import select, func
from aiogram import Bot
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.utils.other.keyboards import cancel_kb, admin_kb, student_kb, yes_or_no_kb
from bot.utils.schedule.update_schedule import refresh_schedule_data
from bot.handlers.states import AdminState
from bot.utils.utils import lazy_get_user_by_chat_id
from database.confdb import session
from database.models import User


router = Router(name=__name__)


@router.message(F.text == "Отправить сообщение всем")
async def send_a_message_to_everyone(message: Message, state: FSMContext) -> None:
    user: User = await lazy_get_user_by_chat_id(
        chat_id=message.chat.id, session=session
    )

    if not user.admin:
        await message.answer(text="Недостаточно прав.", reply_markup=student_kb())
        return

    await message.answer(
        text="Введите сообщение которое хотите отправить:", reply_markup=cancel_kb()
    )
    await state.set_state(AdminState.send_a_message_to_everyone)


@router.message(AdminState.send_a_message_to_everyone)
async def send_a_message_to_everyone_step2(
    message: Message, state: FSMContext, bot: Bot
) -> None:
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.scalars().all()

    if message.text == "Отмена":
        await state.clear()
        await message.answer(text="Операция отменена.", reply_markup=admin_kb())
        return

    for user in users:
        await bot.send_message(chat_id=user.chat_id, text=message.text)
    else:
        await message.answer(
            text="Сообщение успешно отправлено", reply_markup=admin_kb()
        )
        await state.clear()


@router.message(F.text == "Узнать кол-во юзеров")
async def get_count_users(message: Message) -> None:
    user: User = await lazy_get_user_by_chat_id(
        chat_id=message.chat.id, session=session
    )

    if not user.admin:
        await message.answer(text="Недостаточно прав.")
        return

    stmt = select(func.count(User.id))
    result = await session.execute(stmt)
    count = result.scalar()

    await message.answer(text=f"Зарегистрированных пользователей: {count}")


@router.message(F.text == "Обновить расписание")
async def update_schedule_by_admin(message: Message, state: FSMContext) -> None:
    user: User = await lazy_get_user_by_chat_id(
        chat_id=message.chat.id, session=session
    )

    if not user.admin:
        await message.answer(text="Недостаточно прав.", reply_markup=student_kb())
        return

    await message.answer(
        text="Вы уверенны что хотите обновить расписание?", reply_markup=yes_or_no_kb()
    )
    await state.set_state(AdminState.update_schedule)


@router.message(AdminState.update_schedule)
async def update_schedule_by_admin_step2(message: Message, state: FSMContext) -> None:
    if message.text == "Нет ❌":
        await state.clear()
        await message.answer(text="Операция отменена.", reply_markup=admin_kb())
        await state.clear()
        return
    elif message.text == "Да ✅":
        await refresh_schedule_data(session=session)
        await message.answer(
            text="Расписание успешно обновлено.", reply_markup=admin_kb()
        )
        await state.clear()
    else:
        await message.answer(text="Неверное формат ввода.", reply_markup=admin_kb())
        await state.clear()
