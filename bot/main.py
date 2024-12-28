import asyncio

from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.triggers.cron import CronTrigger
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from database.models import User
from database.confdb import session
from bot.utils.other.logger import logger
from bot.utils.getter_variables import API_TOKEN
from middlewares.anti_spam import AntiSpamMiddleware
from bot.utils.utils import lazy_get_user_by_chat_id
from bot.utils.other.keyboards import student_kb, admin_kb
from bot.utils.schedule.update_schedule import refresh_schedule_data
from bot.utils.schedule.sending_reminder_shedule import remind_schedule
from bot.utils.other.text_for_messages import info_messages, welcome_messages
from bot.handlers.registration import router as registration_router, start_registration
from bot.handlers.user_panel import router as user_panel_router
from bot.handlers.admin_panel import router as admin_panel_router
from bot.handlers.reminder_sheduler import router as reminder_sheduler_router


dp = Dispatcher()
dp.update.middleware(AntiSpamMiddleware())
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
scheduler = AsyncIOScheduler()


@dp.message(CommandStart())
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


@dp.message(Command("changedata"))
async def command_changedata(message: Message, state: FSMContext) -> None:
    try:
        user: User = await lazy_get_user_by_chat_id(
            chat_id=message.chat.id, session=session
        )
        await session.delete(user)
        await session.commit()
    except ValueError:
        pass
    logger.info(f"{message.chat.username}:{message.chat.id} ввел /changedata")
    await start_registration(message=message, state=state)


@dp.message(Command("info"))
async def command_info(message: Message) -> None:
    await message.answer(text=info_messages)
    logger.info(f"{message.chat.username}:{message.chat.id} ввел /info")


async def main(session: AsyncSession) -> None:
    dp.include_router(registration_router)
    dp.include_router(user_panel_router)
    dp.include_router(admin_panel_router)
    dp.include_router(reminder_sheduler_router)

    scheduler.add_job(
        remind_schedule, trigger=CronTrigger(minute="*"), args=[session, bot]
    )
    scheduler.add_job(
        refresh_schedule_data, trigger=CronTrigger(hour=0, minute=1), args=[session]
    )
    scheduler.start()

    await dp.start_polling(bot)
    logger.info("Бот запущен.")


if __name__ == "__main__":
    asyncio.run(main(session=session))
