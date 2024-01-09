from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)

main_kb = [
    [KeyboardButton(text='Определить группу')]
    ]


main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True)

sendDoc_kb = [
    [KeyboardButton(text='Составить отчет')]
    ]

sendDoc = ReplyKeyboardMarkup(keyboard=sendDoc_kb,
                           resize_keyboard=True)


report = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text='Количество оценок', callback_data = 'quantity')],
   [InlineKeyboardButton(text='Личные номера студентов', callback_data = 'number')],
   [InlineKeyboardButton(text='Формы контроля', callback_data = 'forms')]
    ])