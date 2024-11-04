from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class ReplyKeyboards:
    @staticmethod
    async def get_menu_install_app() -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Android 📱"), KeyboardButton(text="iPhone 🍏")],
            [KeyboardButton(text="Windows 💻"), KeyboardButton(text="MacOS 💻")],
            [KeyboardButton(text="Телевизор 📺")]
        ], resize_keyboard=True)
        return keyboard

    @staticmethod
    async def get_menu_help() -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Как подключиться ❔")]
        ], resize_keyboard=True)
        return keyboard
