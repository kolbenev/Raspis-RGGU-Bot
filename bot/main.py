import asyncio

from telebot import async_telebot, types
from telebot.types import Message

from bot.keyboards import student_kb
from bot.registration import (
    registered_stage_kyrs,
    register_user,
    registered_stage_formob,
    registered_stage_group,
)
from bot.utils.text_for_messages import welcome_messages, satge_kyrs
from bot.utils.getter_variables import API_TOKEN
from bot.utils.utils import lazy_get_user_by_chat_id
from database.confdb import session
from database.models import User
from bot.getters_schedule import get_today_schedule, get_tomorrow_schedule

bot = async_telebot.AsyncTeleBot(API_TOKEN)


@bot.message_handler(commands=["start"])
async def command_start(message: Message):
    try:
        user: User = await lazy_get_user_by_chat_id(
            chat_id=message.chat.id, session=session
        )
        await bot.send_message(chat_id=message.chat.id, text='Выберите на какой день вы хотите получить расписание:', reply_markup=student_kb())

    except ValueError:
        user: User = await register_user(message=message, session=session)
        user.user_status = "registered_stage_kyrs"
        await session.commit()
        await bot.send_message(chat_id=message.chat.id, text=welcome_messages)
        await bot.send_message(chat_id=message.chat.id, text="Начнем регистрацию, введите ваш курс:")


@bot.message_handler(content_types=["text"])
async def main(message: Message):
    """
    Основной хендлер, который обрабатывает все сообщения.
    """
    user: User = await lazy_get_user_by_chat_id(
        chat_id=message.chat.id, session=session
    )

    if message.text == "📌 На сегодня":
        schedule: str = await get_today_schedule(session=session, chat_id=message.chat.id)
        await bot.send_message(chat_id=message.chat.id, text=schedule)

    if message.text == "🌅 На завтра":
        schedule: str = await get_tomorrow_schedule(session=session, chat_id=message.chat.id)
        await bot.send_message(chat_id=message.chat.id, text=schedule)


    if user.user_status == "registered_stage_kyrs":
        await registered_stage_kyrs(
            message=message, user=user, bot=bot, session=session
        )

    elif user.user_status == "registered_stage_formob":
        await registered_stage_formob(
            message=message, user=user, bot=bot, session=session
        )

    elif user.user_status == "registered_stage_group":
        await registered_stage_group(
            message=message, user=user, bot=bot, session=session
        )

    else:
        await bot.send_message(chat_id=message.chat.id, text="Очень странно....")


if __name__ == "__main__":
    asyncio.run(bot.infinity_polling())
