from telebot import types


def student_kb() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('📌 На сегодня')
    btn2 = types.KeyboardButton('🌅 На завтра')
    kb.row(btn1, btn2)
    return kb