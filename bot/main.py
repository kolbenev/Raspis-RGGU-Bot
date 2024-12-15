"""
Основной модуль бота, в котором происходит его запуск и представлена его базовая
логика работы.
"""

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from telebot import async_telebot, logger
from telebot.types import Message

from database.confdb import session
from database.models import User
from bot.admin_panel import send_message_to_everyone, get_count_users
from bot.other.keyboards import student_kb, admin_kb
from bot.other.text_for_messages import welcome_messages, info_messages
from bot.utils.getter_variables import API_TOKEN
from bot.utils.utils import lazy_get_user_by_chat_id
from bot.schedule.update_schedule import daily_schedule_updater, refresh_schedule_data
from bot.schedule.getters_schedule import (
    get_today_schedule,
    get_tomorrow_schedule,
    get_weekly_schedule,
)
from bot.registration import (
    registered_stage_kyrs,
    register_user,
    registered_stage_formob,
    registered_stage_group,
)


bot = async_telebot.AsyncTeleBot(API_TOKEN)
logger.level = logging.INFO


@bot.message_handler(commands=["start"])
async def command_start(message: Message):
    """
    Обрабатывает команду /start для пользователя.

    - Если пользователь уже зарегистрирован:
        - Проверяет, является ли пользователь администратором.
        - Если пользователь администратор, отображается приветственное сообщение и кнопки администратора.
        - Если пользователь студент, предлагается выбор расписания с помощью клавиатуры.

    - Если пользователь не зарегистрирован:
        - Запускается процесс регистрации с сохранением данных пользователя в базе.
        - Пользователю отправляется приветственное сообщение и запрос на ввод курса.
    """
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
        logger.info(
            f"Зарегистрирован новый пользователь в бд: {message.chat.username}:{user.chat_id}"
        )


@bot.message_handler(commands=["info"])
async def command_info(message: Message):
    """
    Обрабатывает команду /info

    Отправляет пользователю информационное сообщение.
    """
    await bot.send_message(
        chat_id=message.chat.id,
        text=info_messages,
        parse_mode="HTML",
    )
    logger.info(f"{message.chat.username}:{message.chat.id} ввел /info")


@bot.message_handler(commands=["changedata"])
async def changedata(message: Message):
    """
    Обрабатывает команду /changedata

    Позволяет пользователю пройти
    процесс регистрации заново.
    """
    user: User = await lazy_get_user_by_chat_id(
        chat_id=message.chat.id, session=session
    )
    user.status = "registration"
    user.substatus = "registered_stage_kyrs"
    user.formob = None
    user.kyrs = None
    user.gruppa = None
    await session.commit()
    await bot.send_message(
        chat_id=message.chat.id, text="Начнем регистрацию, введите ваш курс:"
    )
    logger.info(
        f"{message.chat.username}:{message.chat.id} начал процесс регистрации заново."
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
    """
    Обрабатывает пользовательские действия, связанные с
    выбором расписания или административными командами.

    - Для всех пользователей:
        - "📌 На сегодня": отправляет расписание на текущий день.
        - "🌅 На завтра": отправляет расписание на следующий день.
        - "📆 На неделю": отправляет расписание на неделю вперед.

    - Для администраторов:
        - "Отправить сообщение всем": активирует режим отправки
          сообщения всем пользователям.
        - "Узнать кол-во юзеров": отправляет информацию
          о числе зарегистрированных пользователей.
        - "Обновить расписание": обновляет расписание в боте.

    """
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

        logger.info(
            f"{message.chat.username}:{message.chat.id} получил расписание на сегодня"
        )
        return True

    if message.text == "🌅 На завтра":
        schedule: str = await get_tomorrow_schedule(
            session=session, chat_id=message.chat.id
        )
        await bot.send_message(
            chat_id=message.chat.id, text=schedule, parse_mode="HTML"
        )

        logger.info(
            f"{message.chat.username}:{message.chat.id} получил расписание на завтра"
        )
        return True

    if message.text == "📆 На неделю":
        schedule: str = await get_weekly_schedule(
            session=session, chat_id=message.chat.id
        )
        await bot.send_message(
            chat_id=message.chat.id, text=schedule, parse_mode="HTML"
        )

        logger.info(
            f"{message.chat.username}:{message.chat.id} получил расписание на неделю"
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
    Обрабатывает все текстовые сообщения от пользователя,
    в зависимости от их статуса и подстатуса.

    - Если пользователь находится на стадии регистрации,
      выполняется соответствующая обработка в зависимости от подстатуса:
        - "registered_stage_kyrs": запрашивает курс пользователя.
        - "registered_stage_formob": запрашивает форму обучения.
        - "registered_stage_group": запрашивает группу пользователя.

    - Если пользователь находится в панели администратора:
        - "send_message_everyone": обрабатывает отправку сообщения всем пользователям.
            - Если текст сообщения не является командой отмены, отправляет
              сообщение всем пользователям.
            - Если текст сообщения является командой отмены, отменяет отправку.
        - "update_schedule": обрабатывает обновление расписания.
            - Если пользователь подтверждает "Да", обновляется расписание.
            - Если пользователь отвечает "Нет", отменяется обновление расписания.
    """
    try:
        user: User = await lazy_get_user_by_chat_id(
            chat_id=message.chat.id, session=session
        )

        if user.status == "registration":
            if user.substatus == "registered_stage_kyrs":
                await registered_stage_kyrs(
                    message=message, user=user, bot=bot, session=session
                )
                logger.info(
                    f"{message.chat.username}:{message.chat.id} проходит регистрацию, субстатус: registered_stage_kyrs"
                )
            elif user.substatus == "registered_stage_formob":
                await registered_stage_formob(
                    message=message, user=user, bot=bot, session=session
                )
                logger.info(
                    f"{message.chat.username}:{message.chat.id} проходит регистрацию, субстатус: registered_stage_formob"
                )
            elif user.substatus == "registered_stage_group":
                await registered_stage_group(
                    message=message, user=user, bot=bot, session=session
                )
                logger.info(
                    f"{message.chat.username}:{message.chat.id} успешно зарегистрировался в боте."
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
                    logger.info(
                        f"{message.chat.username}:{message.chat.id} отправил всем сообщение: '{message.text}'.'"
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
                    logger.info(
                        f"{message.chat.username}:{message.chat.id} обновил расписание в боте через панель администратора."
                    )
                else:
                    await bot.send_message(
                        chat_id=message.chat.id, text="Обновление расписания отменено."
                    )

                user.substatus = None
                await session.commit()
                return True

    except ValueError:
        await command_start(message=message)


async def start(session: AsyncSession):
    """
    Функция для запуска бота.
    """
    asyncio.create_task(daily_schedule_updater(session))
    await bot.infinity_polling()


if __name__ == "__main__":
    logger.info("Бот запущен.")
    asyncio.run(start(session=session))
