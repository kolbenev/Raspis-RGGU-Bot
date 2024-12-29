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
        [
            KeyboardButton(text="Ответить на репорты"),
            KeyboardButton(text="Кол-во репортов"),
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
    kb.append([KeyboardButton(text="⬅ Вернуться назад")])
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        input_field_placeholder="Выберите вашу группу:",
        resize_keyboard=True,
    )
    return keyboard


def time_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text=f"{hour}:00")] for hour in range(7, 24, 4)]
    kb.append([KeyboardButton(text="Отключить напоминание 😥")])
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        input_field_placeholder="Введите или выберите время:",
        resize_keyboard=True,
    )
    return keyboard


def check_report_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Ответить ✅"), KeyboardButton(text="Удалить ❌")],
        [KeyboardButton(text="Выйти")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        input_field_placeholder="Выберите действие:",
        resize_keyboard=True,
    )
    return keyboard


def kyrs_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text=f"{num}")] for num in range(1, 6)]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        input_field_placeholder="Выберите ваш курс:",
        resize_keyboard=True,
    )
    return keyboard


def formob_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Дневная")],
        [KeyboardButton(text="Вечерняя")],
        [KeyboardButton(text="Заочная")],
        [KeyboardButton(text="Второе высшее")],
        [KeyboardButton(text="Магистратура")],
        [KeyboardButton(text="Дистанционная")],
        [KeyboardButton(text="⬅ Вернуться назад")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        input_field_placeholder="Выберите вашу форму обучения:",
        resize_keyboard=True,
    )
    return keyboard
