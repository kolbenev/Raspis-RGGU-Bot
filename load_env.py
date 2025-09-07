"""
Модуль загрузки переменных.
"""

import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
SYNC_DATABASE_URL = os.environ.get("SYNC_DATABASE_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")
ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
BASE_URL = os.environ.get("BASE_URL")
