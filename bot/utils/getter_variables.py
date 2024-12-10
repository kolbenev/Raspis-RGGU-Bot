"""
Модуль для загрузки конфигурационных переменных из файла .env
"""

from dotenv import load_dotenv

from os import getenv

load_dotenv()

API_TOKEN = getenv("API_TOKEN")
