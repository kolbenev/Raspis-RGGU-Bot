"""
Модуль для реализации регистрации пользователя.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot
from parser.parser_main import parsing_schedule

from bot.other.keyboards import student_kb
from bot.other.text_for_messages import stage_formob, stage_grupp_name
from bot.utils.utils import lazy_get_group_by_name, create_new_group
from database.models import User
from config.cafs import caf_id


async def register_user(message: Message, session: AsyncSession) -> User:
    chat_id = message.chat.id
    new_user = User(
        chat_id=chat_id,
        status="registration",
        substatus="registered_stage_kyrs",
    )
    session.add(new_user)
    await session.commit()
    return new_user


async def registered_stage_kyrs(
    message: Message, user: User, bot: AsyncTeleBot, session: AsyncSession
):
    if message.text.isdigit() and 1 <= int(message.text) <= 6:
        user.kyrs = int(message.text)
        user.substatus = "registered_stage_formob"
        await session.commit()
        await bot.send_message(message.chat.id, text=stage_formob)
    else:
        await bot.send_message(
            message.chat.id, text="Неверный ввод курса, попробуй еще раз."
        )


async def registered_stage_formob(
    message: Message, user: User, bot: AsyncTeleBot, session: AsyncSession
):
    formob_list = ["Д", "В", "З", "2", "М", "У"]
    user_answer = message.text.upper()
    if user_answer in formob_list:
        user.formob = user_answer
        user.substatus = "registered_stage_group"
        await session.commit()
        await bot.send_message(
            message.chat.id, text=stage_grupp_name, parse_mode="HTML"
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Неверный ввод формы обучения, попробуйте еще раз!",
        )


async def registered_stage_group(
    user: User, message: Message, bot: AsyncTeleBot, session: AsyncSession
):
    user_answer = message.text
    caf = caf_id[user.formob][user.kyrs][user_answer]
    if caf:
        try:
            group = await lazy_get_group_by_name(
                session=session, group_name=user_answer
            )
            user.gruppa = group.id
            await session.commit()
        except ValueError:
            group = await create_new_group(
                session=session,
                caf=caf,
                name=user_answer,
                kyrs=user.kyrs,
                formob=user.formob,
            )
            user.gruppa = group.id
            await session.commit()
            await parsing_schedule(formob=user.formob, kyrs=user.kyrs, caf=caf)
        finally:
            await bot.send_message(
                message.chat.id,
                text="Успешно зарегистрирован!",
                reply_markup=student_kb(),
            )
            user.substatus = None
            user.status = "student"
            await session.commit()
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Такой группы нет или вы неверно ввели ее название, попробуйте еще раз.",
        )
