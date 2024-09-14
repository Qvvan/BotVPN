from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class ReplyKeyboards:
    @staticmethod
    def start_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура для кнопки 'Оформляем!'"""
        start_button = KeyboardButton(text="Оформляем!")
        return ReplyKeyboardMarkup(
            keyboard=[[start_button]],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    @staticmethod
    def pay_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура для кнопки 'Оплатить'"""
        pay_button = KeyboardButton(text="Оплатить")
        return ReplyKeyboardMarkup(
            keyboard=[[pay_button]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
