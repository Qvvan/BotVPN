from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

start_button = KeyboardButton("Оформляем!")
start_kb = ReplyKeyboardMarkup(
    keyboard=[[start_button]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


pay_button = KeyboardButton("Оплатить")
pay_kb = ReplyKeyboardMarkup(
    keyboard=[[pay_button]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

