from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    gruppa = Column(ForeignKey('groups.id'), nullable=False)
    time_get_schedule = Column(Time, default=None)
    user_status = Column(String, default=None)
    admin = Column(Boolean, default=False)

    group = relationship('Group', back_populates='users')


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String, default=None)
    kaf = Column(String, default=None)

    users = relationship('User', back_populates='group')
    schedule = relationship('Schedule', back_populates='group')


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, autoincrement=True, primary_key=True)
    group_id = Column(ForeignKey('groups.id'), nullable=False)
    date = Column(String)
    para = Column(String)
    lecture_time = Column(String)
    audience = Column(String)
    lesson = Column(String)
    type_lesson = Column(String)
    teacher_name = Column(String)

    group = relationship('Group', back_populates='schedule')