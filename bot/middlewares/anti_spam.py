from functools import wraps
from datetime import datetime, timedelta
import time

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Update, Message

from bot.middlewares.logger import logger


class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 5, block_time: int = 10):
        super().__init__()
        self.limit = limit
        self.block_time = block_time
        self.message_count = {}
        self.blocked_users = {}

    async def __call__(self, handler, event: Update, data: dict):
        user_id = event.message.chat.id
        now = datetime.now()

        self.cleanup_old_records(now)

        if user_id in self.blocked_users:
            block_until = self.blocked_users[user_id]
            if now < block_until:
                await event.message.answer(
                    "Вы присылаете слишком много сообщений, попробуйте чуть позже."
                )
                logger.info(f"{event.message.from_user.username}:{event.message.chat.id}| сработал антиспам.")
                return
            else:
                del self.blocked_users[user_id]

        if user_id not in self.message_count:
            self.message_count[user_id] = []

        self.message_count[user_id].append(now)

        if len(self.message_count[user_id]) > self.limit:
            self.blocked_users[user_id] = now + timedelta(seconds=self.block_time)
            del self.message_count[user_id]
            await event.message.answer(
                "Вы присылаете слишком много сообщений, попробуйте чуть позже."
            )
            logger.info(f"{event.message.from_user.username}:{event.message.chat.id}| сработал антиспам.")
            return

        return await handler(event, data)

    def cleanup_old_records(self, now: datetime):
        """Удаляет старые записи пользователей, которые неактивны."""
        inactive_users = [
            user_id
            for user_id, timestamps in self.message_count.items()
            if timestamps and (now - timestamps[-1]).seconds > self.block_time
        ]
        for user_id in inactive_users:
            del self.message_count[user_id]


class AntiSpam:
    def __init__(self):
        self.blocked_users = {}

    def anti_spam(self, block_time:int):
        def anti_spam_in_report(func):
            @wraps(func)
            async def wrapper(message: Message, state: FSMContext, *args, **kwargs):
                user_id = message.chat.id
                current_time = time.time()

                if func.__name__ not in self.blocked_users:
                    self.blocked_users[func.__name__] = {}

                if user_id in self.blocked_users[func.__name__]:
                    block_time_remaining = self.blocked_users[func.__name__][user_id] - current_time
                    if block_time_remaining > 0:
                        await message.answer(
                            f"Вы сможете воспользоваться этой командой через {int(block_time_remaining)} секунд."
                        )
                        return
                    else:
                        del self.blocked_users[func.__name__][user_id]

                self.blocked_users[func.__name__][user_id] = current_time + block_time
                return await func(message, state, *args, **kwargs)

            return wrapper
        return anti_spam_in_report
