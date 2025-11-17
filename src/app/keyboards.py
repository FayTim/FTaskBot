from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

subjects = {"Математический анализ" : "matan",
            "ООП" : "oop",
            "Python" : "python",
            "Сети" : "network",
            "Дискретная математика" : "discret",
            "Теория вероятностей" : "terver"}
# async def reply_subjects():
#     keyboard = ReplyKeyboardBuilder()
#     for s in subjects:
#         keyboard.add(KeyboardButton(text=s))
#     return keyboard.adjust(2).as_markup()

async def inline_subjects():
    keyboard = InlineKeyboardBuilder()
    for s, k in subjects.items():
        keyboard.add(InlineKeyboardButton(text=s, callback_data=k))
    return keyboard.adjust(2).as_markup()