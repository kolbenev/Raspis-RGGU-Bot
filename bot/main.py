import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from telebot import async_telebot
from telebot.types import Message

from bot.admin_panel import send_message_to_everyone, get_count_users
from bot.utils.keyboards import student_kb, admin_kb
from bot.registration import (
    registered_stage_kyrs,
    register_user,
    registered_stage_formob,
    registered_stage_group,
)
from bot.utils.text_for_messages import welcome_messages, info_messages
from bot.utils.getter_variables import API_TOKEN
from bot.utils.update_schedule import daily_schedule_updater, refresh_schedule_data
from bot.utils.utils import lazy_get_user_by_chat_id
from database.confdb import session
from database.models import User
from bot.utils.getters_schedule import (
    get_today_schedule,
    get_tomorrow_schedule,
    get_weekly_schedule,
)


bot = async_telebot.AsyncTeleBot(API_TOKEN)


@bot.message_handler(commands=["start"])
async def command_start(message: Message):
    try:
        user: User = await lazy_get_user_by_chat_id(
            chat_id=message.chat.id, session=session
        )
        if user.admin is True:
            await bot.send_message(
                chat_id=message.chat.id,
                text=welcome_messages,
                reply_markup=admin_kb(),
            )
            user.status = "admin_panel"
            await session.commit()
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text="Выберите на какой день вы хотите получить расписание:",
                reply_markup=student_kb(),
            )

    except ValueError:
        user: User = await register_user(message=message, session=session)
        await bot.send_message(chat_id=message.chat.id, text=welcome_messages)
        await bot.send_message(
            chat_id=message.chat.id, text="Начнем регистрацию, введите ваш курс:"
        )


@bot.message_handler(commands=["info"])
async def command_info(message: Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text=info_messages,
        parse_mode="HTML",
    )


@bot.message_handler(commands=["changedata"])
async def command_info(message: Message):
    user: User = await lazy_get_user_by_chat_id(chat_id=message.chat.id, session=session)
    user.status = "registration"
    user.substatus = "registered_stage_kyrs"
    user.formob = None
    user.kyrs = None
    user.gruppa = None
    await session.commit()
    await bot.send_message(
        chat_id=message.chat.id,
        text='Начнем регистрацию, введите ваш курс:'
    )


@bot.message_handler(
    func=lambda message: message.text
    in [
        "📌 На сегодня",
        "🌅 На завтра",
        "📆 На неделю",
        "Отправить сообщение всем",
        "Узнать кол-во юзеров",
        "Обновить расписание",
    ]
)
async def user_panel(message: Message):
    user: User = await lazy_get_user_by_chat_id(
        chat_id=message.chat.id, session=session
    )

    if message.text == "📌 На сегодня":
        schedule: str = await get_today_schedule(
            session=session, chat_id=message.chat.id
        )
        await bot.send_message(
            chat_id=message.chat.id, text=schedule, parse_mode="HTML"
        )
        return True

    if message.text == "🌅 На завтра":
        schedule: str = await get_tomorrow_schedule(
            session=session, chat_id=message.chat.id
        )
        await bot.send_message(
            chat_id=message.chat.id, text=schedule, parse_mode="HTML"
        )
        return True

    if message.text == "📆 На неделю":
        schedule: str = await get_weekly_schedule(
            session=session, chat_id=message.chat.id
        )
        await bot.send_message(
            chat_id=message.chat.id, text=schedule, parse_mode="HTML"
        )
        return True

    if (
        message.text
        in ["Отправить сообщение всем", "Узнать кол-во юзеров", "Обновить расписание"]
        and user.admin is True
    ):
        if message.text == "Отправить сообщение всем":
            await bot.send_message(
                chat_id=message.chat.id,
                text="Введите сообщение, которое хотите отправить:",
            )
            user.substatus = "send_message_everyone"
            await session.commit()
            return True

        if message.text == "Узнать кол-во юзеров":
            count_users = await get_count_users(session=session)
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"Зарегистрированных пользователей: {count_users}",
            )
            return True

        if message.text == "Обновить расписание":
            await bot.send_message(
                chat_id=message.chat.id,
                text="Вы уверены что хотите обновить расписание?",
            )
            user.substatus = "update_schedule"
            await session.commit()
            return True


@bot.message_handler(content_types=["text"])
async def main(message: Message):
    """
    Основной хендлер, который обрабатывает все сообщения.
    """
    user: User = await lazy_get_user_by_chat_id(
        chat_id=message.chat.id, session=session
    )

    if user.status == "registration":
        if user.substatus == "registered_stage_kyrs":
            await registered_stage_kyrs(
                message=message, user=user, bot=bot, session=session
            )
        elif user.substatus == "registered_stage_formob":
            await registered_stage_formob(
                message=message, user=user, bot=bot, session=session
            )
        elif user.substatus == "registered_stage_group":
            await registered_stage_group(
                message=message, user=user, bot=bot, session=session
            )

        return True

    if user.status == "admin_panel":
        if user.substatus == "send_message_everyone":
            if message.text not in ["0", "O", "o", "Отмена", "отмена", "о", "О"]:
                await send_message_to_everyone(
                    session=session, bot=bot, message=message
                )
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Сообщение успешно отправлено всем пользователям.",
                )
            else:
                await bot.send_message(
                    chat_id=message.chat.id, text="Отправка сообщения всем отменена!"
                )

            user.substatus = None
            await session.commit()
            return True

        if user.substatus == "update_schedule":
            if message.text == "Да":
                await refresh_schedule_data(session=session)
                await bot.send_message(
                    chat_id=message.chat.id, text="Расписание успешно обновлено."
                )
            else:
                await bot.send_message(
                    chat_id=message.chat.id, text="Обновление расписания отменено."
                )

            user.substatus = None
            await session.commit()
            return True


async def start(session: AsyncSession):
    asyncio.create_task(daily_schedule_updater(session))
    await bot.infinity_polling()


if __name__ == "__main__":
    asyncio.run(start(session=session))
