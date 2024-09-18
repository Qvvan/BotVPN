from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db_methods import MethodsManager
from database.init_db import DataBase


class ServiceCallbackFactory(CallbackData, prefix='service'):
    service_id: str
    service_price: str
    service_name: str
    duration_days: str


class InlineKeyboards:
    @staticmethod
    async def create_order_keyboards() -> InlineKeyboardMarkup:
        """Клавиатура для кнопок с услугами."""
        db = DataBase()
        async with db.Session() as session:
            session_methods = MethodsManager(session)
            services = await session_methods.services.get_services()
            keyboard = InlineKeyboardBuilder()

            buttons: list[InlineKeyboardButton] = []

            for service in services:
                service_id = str(service.service_id)
                service_name = service.name
                service_price = str(service.price)
                duration_days = str(service.duration_days)

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
    async def create_pay(price) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text=f"Оплатить {price} ⭐️", pay=True)

        return keyboard.as_markup()
