"""
Модуль конфигурации базы данных.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from load_env import DATABASE_URL, SYNC_DATABASE_URL


url = DATABASE_URL
engine = create_async_engine(
    url,
    echo=False,
    pool_pre_ping=True,
    future=True,
)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
session = SessionLocal()

# ======= Sync Engine =======

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    future=True,
)
SyncSessionLocal = sessionmaker(bind=sync_engine)
