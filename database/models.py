"""
Модуль моделей базы данных.
"""

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    BigInteger,
    DateTime,
)


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger)
    user_id = Column(BigInteger)
    username = Column(String)
    course = Column(String)
    group_id = Column(String)
    eduform = Column(String)
    teacher_id = Column(String)
    status = Column(String, comment="student/teacher")
    is_admin = Column(Boolean, default=False)
    notify_time = Column(String, nullable=True)
    notify_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
