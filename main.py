"""
Модуль для запуска бота.
"""

import asyncio

from bot.bot_main import start_bot

if __name__ == "__main__":
    asyncio.run(start_bot())
