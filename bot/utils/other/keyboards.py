"""
Модуль в котором собраны клавиатуры для пользователя.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config.cafs import caf_id


def student_kb() -> ReplyKeyboardMarkup:
    kb = [
        [
            KeyboardButton(text="📌 На сегодня"),
            KeyboardButton(text="🌅 На завтра"),
            KeyboardButton(text="📆 На неделю"),
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        input_field_placeholder="Какие расписание вас интересует?",
        resize_keyboard=True,
    )
    return keyboard


def admin_kb() -> ReplyKeyboardMarkup:
    kb = [
        [
            KeyboardButton(text="📌 На сегодня"),
            KeyboardButton(text="🌅 На завтра"),
            KeyboardButton(text="📆 На неделю"),
        ],
        [
            KeyboardButton(text="Отправить сообщение всем"),
            KeyboardButton(text="Узнать кол-во юзеров"),
            KeyboardButton(text="Обновить расписание"),
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        input_field_placeholder="Какие расписание вас интересует?",
        resize_keyboard=True,
    )
    return keyboard


def cancel_kb() -> ReplyKeyboardMarkup:
    kb = [
        [
            KeyboardButton(text="Отмена"),
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        input_field_placeholder="Вы уверены, что хотите сделать это?",
        resize_keyboard=True,
    )
    return keyboard


def yes_or_no_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Да ✅"), KeyboardButton(text="Нет ❌")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        input_field_placeholder="Вы уверены, что хотите сделать это?",
        resize_keyboard=True,
    )
    return keyboard


def group_kb(formob: str, kyrs: int) -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text=group)] for group in caf_id[formob][kyrs].keys()]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        input_field_placeholder="Выберите вашу группу:",
        resize_keyboard=True,
    )
    return keyboard
