from aiogram import BaseMiddleware
from datetime import datetime, timedelta

from aiogram.types import Update


class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 4, block_time: int = 10):
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
                await event.message.answer("Вы присылаете слишком много сообщений, попробуйте чуть позже.")
                return
            else:
                del self.blocked_users[user_id]

        if user_id not in self.message_count:
            self.message_count[user_id] = []

        self.message_count[user_id].append(now)

        if len(self.message_count[user_id]) > self.limit:
            self.blocked_users[user_id] = now + timedelta(seconds=self.block_time)
            del self.message_count[user_id]
            await event.message.answer("Вы присылаете слишком много сообщений, попробуйте чуть позже.")
            return

        return await handler(event, data)

    def cleanup_old_records(self, now: datetime):
        """Удаляет старые записи пользователей, которые неактивны."""
        inactive_users = [
            user_id for user_id, timestamps in self.message_count.items()
            if timestamps and (now - timestamps[-1]).seconds > self.block_time
        ]
        for user_id in inactive_users:
            del self.message_count[user_id]
