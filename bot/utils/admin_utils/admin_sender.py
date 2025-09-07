import asyncio

from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramRetryAfter,
)
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput

from bot.states import AdminStates
from config.logger import logger
from database.confdb import session
from database.utils import get_all_users


async def make_sender(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
):
    """
    Функция для рассылки сообщений
    пользователям от администратора.
    """
    logger.info(
        f"{message.from_user.username}:{message.from_user.id} "
        f"Начал рассылку среди пользователей, текст: {message.text}"
    )

    users = await get_all_users(session)

    if not users:
        await dialog_manager.event.answer(text="❌ В боте нет пользователей!")
        await dialog_manager.switch_to(
            state=AdminStates.main_menu,
            show_mode=ShowMode.DELETE_AND_SEND,
        )
        return

    success_count = 0
    error_count = 0
    skipped_count = 0

    bot = dialog_manager.event.bot

    for user in users:
        try:
            if message.photo:
                await bot.send_photo(
                    chat_id=user.chat_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption or "",
                )
            else:
                await bot.send_message(
                    chat_id=user.chat_id, text=message.text or "Пустое сообщение"
                )
            success_count += 1

        except TelegramForbiddenError:
            logger.warning(f"Пользователь {user.username}:{user.id} заблокировал бота")
            skipped_count += 1

        except TelegramBadRequest as e:
            logger.warning(f"BadRequest для {user.username}:{user.id} — {e}")
            skipped_count += 1

        except TelegramRetryAfter as e:
            logger.warning(
                f"FloodWait {e.retry_after}s при отправке {user.username}:{user.id}"
            )
            await asyncio.sleep(e.retry_after)
            continue

        except Exception as e:
            logger.exception(f"Ошибка при отправке {user.username}:{user.id}: {e}")
            error_count += 1

        await asyncio.sleep(0.07)

    await message.answer(
        text=(
            f"📬 Рассылка завершена!\n"
            f"✅ Успешно: {success_count}\n"
            f"⚠️ Пропущено: {skipped_count}\n"
            f"❌ Ошибки: {error_count}"
        )
    )
    logger.info("Успешно завершаем рассылку.")
    await dialog_manager.switch_to(
        state=AdminStates.main_menu,
        show_mode=ShowMode.DELETE_AND_SEND,
    )
