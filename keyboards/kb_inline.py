from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import DB


class ServiceCallbackFactory(CallbackData, prefix='service'):
    service_id: int
    service_price: int
    service_name: str
    duration_days: str


class InlineKeyboards:
    @staticmethod
    def create_order_keyboards() -> InlineKeyboardMarkup:
        """Клавиатура для кнопок с услугами."""
        services = DB.get().get_services()  # Получаем услуги из базы данных
        keyboard = InlineKeyboardBuilder()

        buttons: list[InlineKeyboardButton] = []

        for service in services:
            service_id = service['id']
            service_name = service['name']
            service_price = service['price']
            duration_days = str(service['duration_days'])

            callback_data = ServiceCallbackFactory(
                service_id=service_id,
                service_price=service_price,
                service_name=service_name,
                duration_days=duration_days,
            ).pack()

            buttons.append(InlineKeyboardButton(text=service_name, callback_data=callback_data))
        keyboard.row(*buttons, width=len(buttons))

        return keyboard.as_markup()


    @staticmethod
    def create_pay(price) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text=f"Оплатить {price} ⭐️", pay=True)

        return keyboard.as_markup()
