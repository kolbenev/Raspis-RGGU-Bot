"""
Модуль для загрузки конфигурационных переменных из файла .env
"""

from os import getenv

from dotenv import load_dotenv


load_dotenv()
API_TOKEN = getenv("API_TOKEN")
