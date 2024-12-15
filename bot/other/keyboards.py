"""
Модуль в котором собраны клавиатуры для пользователя.
"""

from telebot import types


def student_kb() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        input_field_placeholder="Выберите какое расписание вас интересует:",
    )
    btn1 = types.KeyboardButton("📌 На сегодня")
    btn2 = types.KeyboardButton("🌅 На завтра")
    btn3 = types.KeyboardButton("📆 На неделю")
    kb.row(btn1, btn2, btn3)
    return kb


def admin_kb() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        input_field_placeholder="Выберите какое расписание вас интересует:",
    )
    btn1 = types.KeyboardButton("📌 На сегодня")
    btn2 = types.KeyboardButton("🌅 На завтра")
    btn3 = types.KeyboardButton("📆 На неделю")
    btn4 = types.KeyboardButton("Отправить сообщение всем")
    btn5 = types.KeyboardButton("Узнать кол-во юзеров")
    btn6 = types.KeyboardButton("Обновить расписание")
    kb.row(btn1, btn2, btn3)
    kb.row(btn4, btn5, btn6)
    return kb
