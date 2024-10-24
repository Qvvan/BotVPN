from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.context_manager import DatabaseContextManager
from logger.logging_config import logger


class ServiceCallbackFactory(CallbackData, prefix='service'):
    service_id: str


class SubscriptionCallbackFactory(CallbackData, prefix="subscription"):
    action: str
    subscription_id: int


class InlineKeyboards:
    @staticmethod
    async def create_order_keyboards() -> InlineKeyboardMarkup:
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
                    ).pack()

                    buttons.append(InlineKeyboardButton(text=service_name, callback_data=callback_data))
                keyboard.row(*buttons)

                keyboard.row(
                    InlineKeyboardButton(text='Отмена', callback_data='cancel')
                )

                return keyboard.as_markup()
            except Exception as e:
                logger.log_error(f'Произошла ошибка при формирование услуг', e)

    @staticmethod
    async def create_pay(price) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text=f"Оплатить {price} ⭐️", pay=True)
        keyboard.button(text="⭐ Купить звезды ⭐",
                        url='https://telegra.ph/Instrukciya-po-pokupke-zvezd-dlya-VPN-cherez-Telegram-bota-10-22')
        keyboard.button(text="🔙 Назад", callback_data="back_to_services")

        keyboard.adjust(1)

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

    @staticmethod
    async def get_back_button_keyboard() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()

        back_button = InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back_to_support_menu"
        )

        keyboard.add(back_button)

        return keyboard.as_markup()

    @staticmethod
    async def show_start_menu() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()

        know_more_button = InlineKeyboardButton(
            text="Узнать больше",
            callback_data="know_more",
        )
        keyboard.add(know_more_button)

        return keyboard.as_markup()
