"""
Модуль логгирования.
"""

import logging

logger_lever = logging.DEBUG

logger = logging.getLogger(__name__)
logger.setLevel(logger_lever)
console_handler = logging.StreamHandler()
console_handler.setLevel(logger_lever)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("bot_logs.log")
file_handler.setLevel(logger_lever)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
