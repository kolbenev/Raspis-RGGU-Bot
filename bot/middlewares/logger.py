import logging

from aiogram.types import Update
from aiogram import BaseMiddleware


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s|%(levelname)s| %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class LoggingMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.logger = logger

    async def __call__(self, handler, event: Update, data: dict):

        logger.info(
            f"{event.message.from_user.username}:{event.message.chat.id} | Message: {event.message.text}"
        )
        return await handler(event, data)
