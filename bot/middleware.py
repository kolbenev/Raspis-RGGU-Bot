import time
import asyncio
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from collections import defaultdict

from config.logger import logger


class ThrottleMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0, cleanup_interval: int = 60):
        super().__init__()
        self.rate_limit = rate_limit
        self.last_time = defaultdict(float)
        self.cleanup_interval = cleanup_interval

    async def __call__(self, handler, event: TelegramObject, data: dict):
        user_id = getattr(getattr(event, "from_user", None), "id", None)
        if not user_id:
            return await handler(event, data)

        now = time.time()
        last = self.last_time[user_id]

        if now - last < self.rate_limit:
            logger.info(f"⛔ Игнор для {user_id}")
            return
        logger.info(f"✅ Пропускаем {user_id}")


        self.last_time[user_id] = now
        return await handler(event, data)

    async def cleanup_task(self):
        while True:
            await asyncio.sleep(self.cleanup_interval)
            now = time.time()
            to_delete = [uid for uid, ts in self.last_time.items()
                         if now - ts > self.rate_limit * 10]
            for uid in to_delete:
                del self.last_time[uid]

