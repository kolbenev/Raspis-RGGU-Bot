"""
Модуль административной панели.
"""

from sqlalchemy import select, func
from aiogram import Bot
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.middlewares.user_permissions import is_admin
from bot.middlewares.logger import logger
from bot.utils.other.keyboards import cancel_kb, admin_kb, yes_or_no_kb, check_report_kb
from bot.utils.schedule.update_schedule import refresh_schedule_data
from bot.handlers.states import AdminState
from database.confdb import session
from database.models import User, MessagesToAdmin

router = Router(name=__name__)


@router.message(F.text == "Отправить сообщение всем")
@is_admin
async def send_a_message_to_everyone(message: Message, state: FSMContext) -> None:

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
        logger.info(
            f"{message.chat.username}:{message.chat.id} отправил всем сообщение: {message.text}"
        )


@router.message(F.text == "Узнать кол-во юзеров")
@is_admin
async def get_count_users(message: Message, state: FSMContext) -> None:
    stmt = select(func.count(User.id))
    result = await session.execute(stmt)
    count = result.scalar()

    await message.answer(text=f"Зарегистрированных пользователей: {count}")


@router.message(F.text == "Обновить расписание")
@is_admin
async def update_schedule_by_admin(message: Message, state: FSMContext) -> None:
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
        logger.info(
            f"{message.chat.username}:{message.chat.id} обновил расписание в боте через админ панель."
        )
    else:
        await message.answer(text="Неверное формат ввода.", reply_markup=admin_kb())
        await state.clear()


@router.message(F.text == "Кол-во репортов")
@is_admin
async def count_report(message: Message, state: FSMContext) -> None:
    stmt = select(func.count(MessagesToAdmin.id))
    result = await session.execute(stmt)
    count = result.scalar()

    if count:
        await message.answer(text=f"Репортов: {count}")
    else:
        await message.answer(text="Репортов нет")


@router.message(F.text == "Ответить на репорты")
async def check_user_messages(message: Message, state: FSMContext) -> None:
    stmt = select(MessagesToAdmin).order_by(MessagesToAdmin.date_time.asc()).limit(1)
    result = await session.execute(stmt)
    user_report: MessagesToAdmin = result.scalar()

    if not user_report:
        await message.answer(text="Сообщений нет.", reply_markup=admin_kb())
        await state.clear()
        return

    await message.answer(
        text=f"{user_report.messages}\n\nПользователь: {user_report.name}\n"
        f"{user_report.username}:{user_report.chat_id}\n"
        f"{user_report.date_time}\n",
        reply_markup=check_report_kb(),
    )
    await state.update_data(user_report=user_report)
    await state.set_state(AdminState.report_answer)


@router.message(AdminState.report_answer)
async def reply_to_report(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_report = data.get("user_report")

    if message.text == "Ответить ✅":
        await message.answer(
            text="Введите сообщение для пользователя:", reply_markup=cancel_kb()
        )
        await state.set_state(AdminState.report_answer_for_user)

    elif message.text == "Удалить ❌":
        await session.delete(user_report)
        await session.commit()
        await message.answer(text="Репорт удален")
        return await check_user_messages(message, state)

    elif message.text == "Выйти":
        await message.answer(text="Выход из чекера репортов", reply_markup=admin_kb())
        await state.clear()


@router.message(AdminState.report_answer_for_user)
async def report_for_user(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.text == "Отмена":
        await message.answer(text="Отмена отправки сообщения (репорт остается в бд)")
        return await check_user_messages(message, state)

    data = await state.get_data()
    user_report = data.get("user_report")

    await bot.send_message(
        chat_id=user_report.chat_id,
        text=f"👨‍💻 Сообщение от администратора:\n\n {message.text}",
    )
    await message.answer(text="Сообщение успешно отправлено пользователю")
    await session.delete(user_report)
    await session.commit()
    await state.clear()
    return await check_user_messages(message, state)
