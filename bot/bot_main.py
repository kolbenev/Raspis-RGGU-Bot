import asyncio

from aiogram import Dispatcher, Bot, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    ErrorEvent,
)
from aiogram_dialog import (
    DialogManager,
    StartMode,
    setup_dialogs,
    BgManagerFactory,
    ShowMode,
)
from aiogram_dialog.api.exceptions import UnknownIntent
from aiogram_dialog.setup import DialogRegistry
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bot.middleware import ThrottleMiddleware
from bot.states import UserStates
from bot.utils.user_utils.notifications.scheduler import notifications_tick
from config.logger import logger
from database.confdb import session
from database.utils import get_user_by_user_id
from load_env import TELEGRAM_TOKEN
from bot.dialogs.user_dialogs import dialog as user_dialogs
from bot.dialogs.admin_dialogs import dialog as admin_dialogs
from bot.handlers.payments_handler import router as payments_router
from bot.handlers.admin_handlers import router as admin_router


bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dialog_registry = DialogRegistry(dp)
manager_factory: BgManagerFactory = setup_dialogs(dp)
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
throttle_message = ThrottleMiddleware(rate_limit=2.0)
throttle_callback = ThrottleMiddleware(rate_limit=1.0)
dp.message.middleware(throttle_message)
dp.callback_query.middleware(throttle_callback)


async def check_user_and_give_menu(user_id: int, dialog_manager: DialogManager):
    """
    Выдает корректное меню пользователю.
    """
    user = await get_user_by_user_id(user_id=user_id, session=session)
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
        show_mode=ShowMode.DELETE_AND_SEND,
    )


@dp.message(CommandStart())
async def start(
    message: Message,
    state: FSMContext,
    bot: Bot,
    dialog_manager: DialogManager,
):
    """
    Обработчик команды /start:
    определяет состояние пользователя и запускает меню.
    """
    try:
        await dialog_manager.done()
    except Exception:
        pass

    logger.debug(f"{message.from_user.username}:{message.from_user.id} ввел /start")

    try:
        await message.delete()
    except Exception:
        pass

    await check_user_and_give_menu(
        user_id=message.from_user.id,
        dialog_manager=dialog_manager,
    )


@dp.errors(
    ExceptionTypeFilter(UnknownIntent),
    F.update.callback_query.as_("callback_query"),
)
async def unknown_intent_handler(
    event: ErrorEvent,
    callback_query: CallbackQuery,
    dialog_manager: DialogManager,
):
    """
    Обработка ошибки UnknownIntent.
    """
    await check_user_and_give_menu(
        user_id=callback_query.message.from_user.id,
        dialog_manager=dialog_manager,
    )


async def start_bot():
    """
    Запустить бота: настроить планировщик уведомлений,
    подключить роутеры и начать polling.
    """
    scheduler.add_job(
        notifications_tick,
        trigger=CronTrigger(minute=5),
        args=(
            bot,
            manager_factory,
        ),
    )
    scheduler.start()
    logger.info("Бот запущен.")
    asyncio.create_task(throttle_message.cleanup_task())
    asyncio.create_task(throttle_callback.cleanup_task())
    dp.include_router(admin_router)
    dp.include_router(payments_router)
    dp.include_router(user_dialogs)
    dp.include_router(admin_dialogs)

    await dp.start_polling(bot)
