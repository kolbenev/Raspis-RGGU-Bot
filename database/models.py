"""
Модуль моделей.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Time,
    Boolean,
    ForeignKey,
    BigInteger,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    """
    Модель для представления пользователя в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        chat_id (int): Идентификатор чата в Telegram.
        gruppa (int, ForeignKey): Ссылка на группу, к которой принадлежит пользователь.
        formob (str): Форма обучения.
        kyrs (int): Курс, на котором учится пользователь.
        status (str): Статус пользователя.
        substatus (str): Дополнительный статус пользователя, используемый для управления состоянием.
        admin (bool): Флаг, показывающий, является ли пользователь администратором.

    Связи:
        group (Group): Группа, к которой принадлежит пользователь.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)
    gruppa = Column(ForeignKey("groups.id"), default=None)
    formob = Column(String(1), default=None)
    kyrs = Column(Integer(), default=None)
    reminder = Column(Time)
    admin = Column(Boolean, default=False)

    group = relationship("Group", back_populates="users")


class Group(Base):
    """
    Модель для представления учебной группы в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор группы.
        name (str): Название группы.
        caf (str): ID кафедры.
        kyrs (int): Курс учебной группы.
        formob (str): Форма обучения группы.

    Связи:
        users (User): Список пользователей, принадлежащих к данной группе.
        schedule (Schedule): Расписание для данной группы.
    """

    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String, default=None)
    caf = Column(String, default=None)
    kyrs = Column(Integer, default=None)
    formob = Column(String(1), default=None)

    users = relationship("User", back_populates="group")
    schedule = relationship("Schedule", back_populates="group")


class Schedule(Base):
    """
    Модель для представления расписания группы в базе данных.

    Атрибуты:
        id (int): Уникальный идентификатор записи расписания.
        group_id (int, ForeignKey): Ссылка на группу, для которой составлено расписание.
        date (str): Дата занятия (например, '20.12.2024 ПТ').
        para (str): Номер пары.
        lecture_time (str): Время занятия.
        audience (str): Номер аудитории, где проходит занятие.
        lesson (str): Название дисциплины.
        type_lesson (str): Тип занятия.
        teacher_name (str): Имя преподавателя.

    Связи:
        group (Group): Группа, для которой составлено расписание.
    """

    __tablename__ = "schedules"

    id = Column(Integer, autoincrement=True, primary_key=True)
    group_id = Column(ForeignKey("groups.id"), nullable=False)
    date = Column(String)
    para = Column(String)
    lecture_time = Column(String)
    audience = Column(String)
    lesson = Column(String)
    type_lesson = Column(String)
    teacher_name = Column(String)

    group = relationship("Group", back_populates="schedule")


class MessagesToAdmin(Base):
    """
    Модель для предоставления сообщений администратору.

    Атрибуты:
        id (int): Уникальный идентификатор сообщения.
        chat_id (int): ID чата пользователя.
        username (str): Имя пользователя, отправившего сообщение.
        name (str): Полное имя пользователя.
        date_time (datetime): Дата и время создания сообщения.
        messages (str): Текст сообщения.
    """

    __tablename__ = "messages_to_admin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False)
    username = Column(String)
    name = Column(String)
    date_time = Column(DateTime, default=datetime.now())
    messages = Column(String)
