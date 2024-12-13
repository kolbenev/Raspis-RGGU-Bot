"""
Модуль для загрузки конфигурационных переменных из файла .env
"""

from dotenv import load_dotenv

from os import getenv

load_dotenv()

POSTGRES_USER = getenv("POSTGRES_USER")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_DB = getenv("POSTGRES_DB")
HOSTNAME = getenv("HOSTNAME")
