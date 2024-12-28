"""
Панель пользователя.
"""

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.handlers.registration import start_registration
from bot.handlers.states import UserState
from bot.middlewares.anti_spam import AntiSpamInReport
from bot.middlewares.user_permissions import is_registered
from bot.utils.other.keyboards import admin_kb, student_kb, cancel_kb
from bot.utils.other.text_for_messages import welcome_messages
from bot.utils.utils import lazy_get_user_by_chat_id
from database.confdb import session
from bot.utils.other.logger import logger
from bot.utils.schedule.getters_schedule import (
    get_today_schedule,
    get_tomorrow_schedule,
    get_weekly_schedule,
)
from database.models import User, MessagesToAdmin


router = Router(name=__name__)
antispam = AntiSpamInReport()


@router.message(F.text == "📌 На сегодня")
async def schedule_for_today(message: Message) -> None:
    schedule: str = await get_today_schedule(session=session, chat_id=message.chat.id)
    await message.answer(text=schedule)
    logger.info(
        f"{message.chat.username}:{message.chat.id} получил расписание на сегодня."
    )


@router.message(F.text == "🌅 На завтра")
async def schedule_for_today(message: Message) -> None:
    schedule: str = await get_tomorrow_schedule(
        session=session, chat_id=message.chat.id
    )
    await message.answer(text=schedule)
    logger.info(
        f"{message.chat.username}:{message.chat.id} получил расписание на завтра."
    )


@router.message(F.text == "📆 На неделю")
async def schedule_for_today(message: Message) -> None:
    schedule: str = await get_weekly_schedule(session=session, chat_id=message.chat.id)
    await message.answer(text=schedule)
    logger.info(
        f"{message.chat.username}:{message.chat.id} получил расписание на неделю."
    )


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"{message.chat.username}:{message.chat.id} ввел /start")
    try:
        user: User = await lazy_get_user_by_chat_id(
            chat_id=message.chat.id, session=session
        )

        if user.admin:
            await message.answer(
                text="Выдана административная панель", reply_markup=admin_kb()
            )
        else:
            await message.answer(
                text=welcome_messages,
                reply_markup=student_kb(),
            )

    except ValueError:
        await start_registration(message=message, state=state)


@router.message(Command("changedata"))
@is_registered
async def command_changedata(message: Message, state: FSMContext) -> None:
    logger.info(f"{message.chat.username}:{message.chat.id} ввел /changedata")
    await start_registration(message=message, state=state)


@router.message(Command("report"))
@is_registered
@antispam.anti_spam_in_report
async def command_report(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="Введите сообщения для администратора: ", reply_markup=cancel_kb()
    )
    await state.set_state(UserState.report)


@router.message(UserState.report)
async def command_report_part2(message: Message, state: FSMContext) -> None:
    if message.text == "Отмена":
        await state.clear()
        await message.answer(
            text="Отправка сообщения отменена.", reply_markup=student_kb()
        )
        del antispam.blocked_users[message.chat.id]
        return

    new_messages = MessagesToAdmin(
        chat_id=message.chat.id,
        username=message.from_user.username,
        name=message.from_user.first_name,
        messages=message.text,
    )
    session.add(new_messages)
    await session.commit()

    await message.answer(
        text="Ваше сообщение успешно доставлено администратору ✅", reply_markup=student_kb()
    )
    await state.clear()
