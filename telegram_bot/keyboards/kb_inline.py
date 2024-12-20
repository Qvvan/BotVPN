from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.context_manager import DatabaseContextManager
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from models.models import NameApp, SubscriptionStatusEnum


class ServerCallbackData(CallbackData, prefix="server_disable"):
    action: str
    server_ip: str


class UserPaginationCallback(CallbackData, prefix="user"):
    page: int
    action: str


class UserSelectCallback(CallbackData, prefix="user_select"):
    user_id: int


class ServiceCallbackFactory(CallbackData, prefix='service'):
    service_id: str
    status_pay: str


class SubscriptionCallbackFactory(CallbackData, prefix="subscription"):
    action: str
    subscription_id: Optional[int] = None
    name_app: Optional[str] = None


class ReplaceServerCallbackFactory(CallbackData, prefix="serv"):
    action: str
    subscription_id: Optional[int] = None
    server_ip: str


class ServerSelectCallback(CallbackData, prefix="servers"):
    server_ip: str
    server_name: str


class GuideSelectCallback(CallbackData, prefix="guide"):
    action: str
    name_oc: str
    name_app: str


class StatusPay(Enum):
    NEW = "new"
    OLD = "old"


class InlineKeyboards:
    @staticmethod
    async def create_order_keyboards(status_pay: StatusPay) -> InlineKeyboardMarkup:
        """Клавиатура для кнопок с услугами."""
        async with DatabaseContextManager() as session_methods:
            try:
                keyboard = InlineKeyboardBuilder()
                services = await session_methods.services.get_services()
                buttons: list[InlineKeyboardButton] = []

                for service in services:
                    service_id = str(service.service_id)
                    service_name = service.name

                    callback_data = ServiceCallbackFactory(
                        service_id=service_id,
                        status_pay=status_pay.value
                    ).pack()

                    buttons.append(InlineKeyboardButton(text=service_name, callback_data=callback_data))
                keyboard.row(*buttons)

                keyboard.row(
                    InlineKeyboardButton(text='Отмена', callback_data='cancel')
                )

                return keyboard.as_markup()
            except Exception as e:
                await logger.log_error(f'Произошла ошибка при формирование услуг', e)

    @staticmethod
    async def get_servers(ip) -> InlineKeyboardMarkup | int:
        async with DatabaseContextManager() as session_methods:
            try:
                keyboard = InlineKeyboardBuilder()
                servers = await session_methods.servers.get_all_servers()
                buttons: list[InlineKeyboardButton] = []

                for server in servers:
                    if server.hidden == 1:
                        continue
                    server_ip = server.server_ip
                    server_name = server.name

                    callback_data = ServerSelectCallback(
                        server_ip=server_ip,
                        server_name=server_name
                    ).pack()

                    buttons.append(InlineKeyboardButton(
                        text=server_name if server_ip != ip else server_name + "(Текущий)",
                        callback_data=callback_data))

                if len(buttons) == 0:
                    return 0
                keyboard.row(*buttons)

                keyboard.row(
                    InlineKeyboardButton(text='Отмена', callback_data='cancel')
                )

                keyboard.adjust(1)

                return keyboard.as_markup()
            except Exception as e:
                await logger.log_error(f'Произошла ошибка при формирование услуг', e)

    @staticmethod
    async def create_pay(price) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text=f"Оплатить {price} ⭐️", pay=True)
        keyboard.button(text="⭐ Купить звезды ⭐",
                        url='https://telegra.ph/Instrukciya-po-pokupke-zvezd-dlya-VPN-cherez-Telegram-bota-10-22')
        keyboard.button(text="🔙 Назад", callback_data="back_to_services")

        keyboard.adjust(1, 2)

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
            callback_data="back_to_device_selection"
        )

        keyboard.row(support_button)
        keyboard.row(vpn_issue_button)
        keyboard.row(low_speed_button)
        keyboard.row(install_guide_button)

        return keyboard.as_markup()

    @staticmethod
    async def cancel() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='Отменить', callback_data='cancel'))
        return keyboard.as_markup()

    @staticmethod
    async def menu_subs(subscription_id, name_app, server_ip):
        async with DatabaseContextManager() as session_methods:
            try:
                keyboard = InlineKeyboardBuilder()
                subscription = await session_methods.subscription.get_subscription_by_id(subscription_id)
                if subscription.status == SubscriptionStatusEnum.ACTIVE:
                    keyboard.add(
                        InlineKeyboardButton(
                            text='🆕 Сменить локацию',
                            callback_data=ReplaceServerCallbackFactory(
                                action='rep_serv',
                                subscription_id=subscription_id,
                                server_ip=server_ip
                            ).pack()),
                        InlineKeyboardButton(
                            text='🔄 Сменить приложение',
                            callback_data=SubscriptionCallbackFactory(
                                action='replace_app',
                                subscription_id=subscription_id,
                                name_app=name_app
                            ).pack())
                    )
                keyboard.add(
                    InlineKeyboardButton(
                        text='⏳ Продлить подписку',
                        callback_data=SubscriptionCallbackFactory(
                            action='extend_subscription',
                            subscription_id=subscription_id
                        ).pack())
                    )

                keyboard.adjust(2, 1)

                return keyboard.as_markup()
            except Exception as e:
                await logger.log_error(f'Произошла ошибка при формирование клавиатуры с подпиской', e)

    @staticmethod
    async def get_back_button_keyboard(callback: str = "back_to_support_menu") -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()

        back_button = InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=callback
        )

        keyboard.add(back_button)

        return keyboard.as_markup()

    @staticmethod
    async def show_start_menu() -> InlineKeyboardMarkup:
        """Клавиатура для стартового меню."""
        keyboard = InlineKeyboardBuilder()

        # Кнопка "Узнать больше"
        know_more_button = InlineKeyboardButton(
            text="Узнать больше",
            callback_data="know_more",
        )

        # Кнопка "Оформить подписку"
        subscribe_button = InlineKeyboardButton(
            text="Оформить подписку",
            callback_data="subscribe"
        )

        # Добавляем кнопки в клавиатуру
        keyboard.add(know_more_button, subscribe_button)

        return keyboard.as_markup()

    @staticmethod
    async def support_and_subscribe_keyboard() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()

        # Кнопка для обращения в поддержку
        support_button = InlineKeyboardButton(
            text="Поддержка",
            callback_data="support_callback"
        )

        # Кнопка для оформления подписки
        subscribe_button = InlineKeyboardButton(
            text="Оформить подписку",
            callback_data="subscribe"
        )

        keyboard.add(support_button, subscribe_button)

        # Располагаем кнопки в одну строку
        keyboard.adjust(2)

        return keyboard.as_markup()

    @staticmethod
    async def get_guide(turn_on: str = None) -> InlineKeyboardMarkup:
        # Создаем клавиатуру с кнопкой "Инструкция"
        keyboard = InlineKeyboardBuilder()

        instruction_button = InlineKeyboardButton(
            text="Инструкция 📖",
            url=LEXICON_RU['outline_info']  # Ссылка на инструкцию
        )
        keyboard.add(instruction_button)

        if turn_on:
            back_button = InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back_to_support_menu"
            )
            keyboard.add(back_button)

        keyboard.adjust(1)

        return keyboard.as_markup()

    @staticmethod
    async def create_user_pagination_with_users_keyboard(users, page: int, has_next: bool) -> InlineKeyboardMarkup:
        buttons = [[
            InlineKeyboardButton(text="Add all ✅", callback_data="add_all_users"),
            InlineKeyboardButton(text="Add subs ✅", callback_data="add_active_users")
        ]]

        # Кнопки для пользователей
        for user in users:
            buttons.append([InlineKeyboardButton(
                text=f"{user['username']} ({user['user_id']}) {'✅' if user['selected'] else ''}",
                callback_data=UserSelectCallback(user_id=user['user_id']).pack()
            )])

        # Кнопки пагинации
        pagination_buttons = [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=UserPaginationCallback(
                    page=page,
                    action="previous"
                ).pack()) if page > 1 else InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="noop"),
            InlineKeyboardButton(
                text=f"{page}",
                callback_data="noop"
            ),
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=UserPaginationCallback(
                    page=page,
                    action="next"
                ).pack()) if has_next else InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data="noop"
            ),
        ]
        pagination_buttons = [button for button in pagination_buttons if button is not None]

        buttons.append(pagination_buttons)

        buttons.append([InlineKeyboardButton(text="Отменить всех ❌", callback_data="cancel_all")])
        buttons.append([InlineKeyboardButton(text="Сохранить", callback_data="save")])
        buttons.append([InlineKeyboardButton(text='Отменить', callback_data='cancel')])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    async def show_notify_change_cancel() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()

        edit_message = InlineKeyboardButton(text="✏️ Изменить текст", callback_data="edit_message")
        send_notification = InlineKeyboardButton(text="📤 Отправить уведомление", callback_data="send_notification")
        cancel_button = InlineKeyboardButton(text='Отменить', callback_data='cancel')

        # Добавляем кнопки "Изменить текст" и "Отправить уведомление" в одну строку
        keyboard.add(edit_message, send_notification)
        # Вставляем кнопку "Отменить" в новую строку
        keyboard.add(cancel_button)

        # Настройка: максимум по две кнопки в строке
        keyboard.adjust(2)

        return keyboard.as_markup()

    @staticmethod
    async def replace_app(name_app) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        if name_app == NameApp.OUTLINE:
            button = InlineKeyboardButton(text="VLESS", callback_data=SubscriptionCallbackFactory(
                action='name_app', name_app="VLESS").pack())
        else:
            button = InlineKeyboardButton(text="OUTLINE", callback_data=SubscriptionCallbackFactory(
                action='name_app', name_app="OUTLINE").pack())
        keyboard.add(button)

        return keyboard.as_markup()

    @staticmethod
    async def show_guide(name_app) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        vless = InlineKeyboardButton(text="VLESS", callback_data=GuideSelectCallback(
            action='show_guide', name_oc=name_app, name_app='vless').pack())
        outline = InlineKeyboardButton(text="OUTLINE", callback_data=GuideSelectCallback(
            action='show_guide', name_oc=name_app, name_app='outline').pack())
        back = InlineKeyboardButton(text="Назад", callback_data=GuideSelectCallback(
            action='show_guide', name_oc=name_app, name_app='back').pack())
        keyboard.row(vless, outline)
        keyboard.add(back)
        keyboard.adjust(2, 1)

        return keyboard.as_markup()

    @staticmethod
    async def server_management_options(server_ip, hidden_status) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        if hidden_status == 0:
            show_status = InlineKeyboardButton(
                text="Выключить сервер",
                callback_data=ServerCallbackData(action="disable", server_ip=server_ip).pack()
            )
        else:
            show_status = InlineKeyboardButton(
                text="Включить сервер",
                callback_data=ServerCallbackData(action="enable", server_ip=server_ip).pack()
            )
        server_name = InlineKeyboardButton(
            text="Изменить имя",
            callback_data=ServerCallbackData(action="change_name", server_ip=server_ip).pack()
        )
        server_limit = InlineKeyboardButton(
            text="Изменить лимит",
            callback_data=ServerCallbackData(action="change_limit", server_ip=server_ip).pack()
        )
        keyboard.add(show_status, server_name, server_limit)

        return keyboard.as_markup()
