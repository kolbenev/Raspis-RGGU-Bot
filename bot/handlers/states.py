"""
Модуль состояний.
"""

from aiogram.fsm.state import StatesGroup, State


class RegistrationState(StatesGroup):
    kyrs = State()
    formob = State()
    grupp = State()


class AdminState(StatesGroup):
    send_a_message_to_everyone = State()
    quantity_of_users = State()
    update_schedule = State()
    report_answer = State()
    check_report = State()
    report_answer_for_user = State()


class UserState(StatesGroup):
    reminder = State()
    report = State()
