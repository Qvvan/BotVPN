from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.context_manager import DatabaseContextManager
from database.db_methods import MethodsManager
from database.init_db import DataBase
from outline.outline_manager.outline_manager import OutlineManager


class ServiceCallbackFactory(CallbackData, prefix='service'):
    service_id: str
    service_price: str
    service_name: str
    duration_days: str
    server_id: str


class InlineKeyboards:
    @staticmethod
    async def create_order_keyboards(server_id) -> InlineKeyboardMarkup:
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
                    server_id=server_id
                ).pack()

                buttons.append(InlineKeyboardButton(text=service_name, callback_data=callback_data))
            keyboard.row(*buttons)

            keyboard.row(
                InlineKeyboardButton(text='Назад', callback_data='back_to_servers'),
                InlineKeyboardButton(text='Отмена', callback_data='cancel')
            )

            return keyboard.as_markup()

    @staticmethod
    async def create_pay(price) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text=f"Оплатить {price} ⭐️", pay=True)

        return keyboard.as_markup()

    @staticmethod
    async def get_support() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()

        support_user_id = "qvvan"
        support_link = f"t.me/{support_user_id}"

        # Создание кнопки со ссылкой на пользователя
        support_button = InlineKeyboardButton(
            text="Связаться с поддержкой 🛠️",
            url=support_link
        )

        keyboard.add(support_button)
        return keyboard.as_markup()

    @staticmethod
    async def cancel() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='Отменить', callback_data='cancel'))
        return keyboard.as_markup()

    @staticmethod
    async def server_selection_keyboards() -> InlineKeyboardMarkup:
        """Клавиатура для выбора серверов."""
        keyboard = InlineKeyboardBuilder()
        manager = OutlineManager()
        await manager.wait_for_initialization()
        servers = await manager.list_servers()

        async with DatabaseContextManager() as session_methods:
            try:
                keys = await session_methods.vpn_keys.get_keys()
            except Exception as e:
                raise Exception(f'Ошибка при получении ключей: {e}')

        count_server_keys = {}
        for obj in keys:
            if obj.server_name not in count_server_keys:
                count_server_keys[obj.server_name] = 0
            count_server_keys[obj.server_name] += 1

        for server_id, server_name in servers.items():
            n = count_server_keys.get(server_name, 0)
            callback_data = f"select_server:{server_id}:{n}"
            keyboard.add(InlineKeyboardButton(text=f"{server_name}\nДоступно: {n} ключей", callback_data=callback_data))

        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
        keyboard.adjust(1)

        return keyboard.as_markup()
