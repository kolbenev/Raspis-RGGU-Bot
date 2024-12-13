"""
Модуль конфигурации базы данных.
"""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from database.getter_variables import (
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
    HOSTNAME,
)


url = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOSTNAME}:5432/{POSTGRES_DB}"
engine = create_async_engine(url=url)
Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
session = Session()
