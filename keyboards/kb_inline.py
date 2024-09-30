from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.context_manager import DatabaseContextManager
from database.db_methods import MethodsManager
from database.init_db import DataBase
from logger.logging_config import logger
from outline.outline_manager.outline_manager import OutlineManager


class ServiceCallbackFactory(CallbackData, prefix='service'):
    service_id: str
    server_id: str


class ServerCallbackFactory(CallbackData, prefix='select_server'):
    server_id: str
    available_keys: int


class SubscriptionCallbackFactory(CallbackData, prefix="subscription"):
    action: str
    subscription_id: int


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

                callback_data = ServiceCallbackFactory(
                    service_id=service_id,
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

        support_user_id = "Masknet_Support"
        support_link = f"t.me/{support_user_id}"

        # Кнопка для связи с поддержкой
        support_button = InlineKeyboardButton(
            text="Связаться с поддержкой 🛠️",
            url=support_link
        )

        # Новые кнопки с добавленными смайликами
        vpn_issue_button = InlineKeyboardButton(
            text="VPN Не работает ❌",
            callback_data="vpn_issue"
        )
        low_speed_button = InlineKeyboardButton(
            text="Низкая скорость 🐢",
            callback_data="low_speed"
        )
        install_guide_button = InlineKeyboardButton(
            text="Инструкция по установке 📄",
            callback_data="install_guide"
        )

        # Добавляем кнопки в отдельные строки
        keyboard.row(support_button)          # Первая строка
        keyboard.row(vpn_issue_button)        # Вторая строка
        keyboard.row(low_speed_button)        # Третья строка
        keyboard.row(install_guide_button)    # Четвертая строка

        return keyboard.as_markup()

    @staticmethod
    async def cancel() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='Отменить', callback_data='cancel'))
        return keyboard.as_markup()

    @staticmethod
    async def server_selection_keyboards(not_show_server: bool = True) -> InlineKeyboardMarkup:
        """Клавиатура для выбора серверов."""
        keyboard = InlineKeyboardBuilder()
        manager = OutlineManager()
        await manager.wait_for_initialization()
        servers = await manager.list_servers()

        async with DatabaseContextManager() as session_methods:
            try:
                keys = await session_methods.vpn_keys.get_keys()
            except Exception as e:
                logger.error(f'Ошибка при получении ключей: {e}')
                raise

        count_server_keys = {}
        for obj in keys:
            if obj.server_name not in count_server_keys:
                count_server_keys[obj.server_name] = 0
            count_server_keys[obj.server_name] += 1

        for server_id, server_name in servers.items():
            n = count_server_keys.get(server_name, 0)
            if n == 0 and not_show_server:
                continue
            callback_data = f"select_server:{server_id}:{n}"
            keyboard.add(InlineKeyboardButton(text=f"{server_name}\nДоступно: {n} ключей", callback_data=callback_data))

        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
        keyboard.adjust(1)

        return keyboard.as_markup()

    @staticmethod
    async def extend_subscription(subscription_id: int) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(
            text='🔄 Продлить подписку',
            callback_data=SubscriptionCallbackFactory(
                action='extend_subscription',
                subscription_id=subscription_id,
            ).pack()
        ))
        return keyboard.as_markup()

    @staticmethod
    async def extend_subscription_options(subscription_id) -> InlineKeyboardMarkup:

        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(
                text='🔄 Продлить',
                callback_data=SubscriptionCallbackFactory(
                    action='extend_with_key',
                    subscription_id=subscription_id
                ).pack()),
            InlineKeyboardButton(
                text='🆕 Новая услуга',
                callback_data=SubscriptionCallbackFactory(
                    action='new_order',
                    subscription_id=subscription_id
                ).pack()),
        )
        return keyboard.as_markup()
