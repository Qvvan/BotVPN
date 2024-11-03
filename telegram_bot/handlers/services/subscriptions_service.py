import random
from datetime import datetime, timedelta

from aiogram.types import Message

from database.context_manager import DatabaseContextManager
from handlers.services.create_subscription_service import SubscriptionService
from handlers.services.create_transaction_service import TransactionService
from handlers.services.get_session_cookies import get_session_cookie
from handlers.services.key_create import ShadowsocksKeyManager
from keyboards.kb_inline import InlineKeyboards
from keyboards.kb_reply.kb_inline import ReplyKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from models.models import Subscriptions, SubscriptionStatusEnum, SubscriptionsHistory, NameApp


class SubscriptionsService:
    """
    Сервис для обработки подписок в системе.

    Этот класс управляет процессом создания и продления подписок, а также обработкой транзакций.
    """

    @staticmethod
    async def process_new_subscription(message: Message):
        """
        Обрабатывает новую подписку при успешном платеже.

        Принимает сообщение с информацией о платеже, создает транзакцию и подписку,
        а затем отправляет пользователю уведомление с ключом доступа.

        Args:
            message (telegram.Message): Сообщение от Telegram, содержащее информацию о платеже.

        Raises:
            Exception: Если не удалось сохранить транзакцию или создать подписку.
        """
        async with DatabaseContextManager() as session_methods:
            try:
                # Извлечение информации о платеже из сообщения
                in_payload = message.successful_payment.invoice_payload.split(':')
                duration_date = in_payload[1]
                user_id = message.from_user.id
                username = message.from_user.username

                transaction_state = await TransactionService.create_transaction(
                    message, 'successful', 'successful', session_methods
                )
                if not transaction_state:
                    raise Exception("Ошибка сохранения транзакции")

                server_ips = await session_methods.servers.get_all_servers()
                if server_ips:
                    random_server = random.choice(server_ips)
                    server_ip = random_server.server_ip
                else:
                    raise Exception("В базе данных нет ни одного сервера")

                session_cookie = await get_session_cookie(server_ip)
                shadowsocks_manager = ShadowsocksKeyManager(server_ip, session_cookie)
                key, key_id = shadowsocks_manager.manage_shadowsocks_key(
                    tg_id=str(user_id),
                    username=username,
                )

                subscription_created = await SubscriptionService.create_subscription(
                    message, key, key_id, server_ip, session_methods
                )
                if not subscription_created:
                    raise Exception("Ошибка создания подписки")

                await session_methods.session.commit()
                await SubscriptionsService.send_success_response(message, key)
                await logger.log_info(f"Пользователь: @{message.from_user.username}\n"
                                      f"Оформил подписку на {duration_date} дней")

            except Exception as e:
                await logger.log_error(f"Пользователь: @{message.from_user.username}\n"
                                       f"Error during transaction processing", e)
                await message.answer(text="К сожалению, покупка отменена.\nОбратитесь в техподдержку.")
                await SubscriptionsService.refund_payment(message)

                # Откат транзакции
                await session_methods.session.rollback()

                shadowsocks_manager.delete_key(key_id)

                # Сохранение транзакции с отменой
                await TransactionService.create_transaction(
                    message, status='отмена', description=str(e), session_methods=session_methods
                )
                await session_methods.session.commit()

    @staticmethod
    async def extend_sub_successful_payment(message: Message):
        """
        Обрабатывает успешное продление подписки для пользователя.

        Args:
            message (Message): Сообщение от Telegram, содержащее информацию о платеже.
        """
        async with DatabaseContextManager() as session_methods:
            try:
                in_payload = message.successful_payment.invoice_payload.split(':')
                service_id = int(in_payload[0])
                durations_days = in_payload[1]
                subscription_id = int(in_payload[3])

                # Получение текущей подписки пользователя
                subs = await session_methods.subscription.get_subscription(message.from_user.id)
                if subs:
                    transaction_state = await TransactionService.create_transaction(
                        message, 'successful', 'successful', session_methods
                    )
                    if not transaction_state:
                        raise Exception("Ошибка сохранения транзакции")

                    for sub in subs:
                        if sub.subscription_id == subscription_id:
                            subscription_data = {
                                "user_id": message.from_user.id,
                                "service_id": service_id,
                                "dynamic_key": sub.dynamic_key,
                                "start_date": datetime.now(),
                                "end_date": datetime.now() + timedelta(days=int(durations_days)),
                                "updated_at": datetime.now(),
                                "status": SubscriptionStatusEnum.ACTIVE
                            }

                            subscription = Subscriptions(**subscription_data)
                            subscription_history = SubscriptionsHistory(**subscription_data)

                            await session_methods.subscription.update_sub(subscription)
                            await session_methods.subscription.create_sub(subscription_history)
                            await message.answer(text=LEXICON_RU['subscription_renewed'])
                            await session_methods.session.commit()
                            await logger.log_info(f"Пользователь: @{message.from_user.username}\n"
                                                  f"Продлил подписку на {durations_days} дней")
                else:
                    await message.answer(text="Подписка не найдена. Проверьте данные.")

            except Exception as e:
                await logger.log_error(f"Пользователь: @{message.from_user.username}\n"
                                       f"Error during transaction processing", e)
                await message.answer(text="К сожалению, покупка отменена.\nОбратитесь в техподдержку.")

                await SubscriptionsService.refund_payment(message)

                await session_methods.session.rollback()

                await TransactionService.create_transaction(
                    message, status='отмена', description=str(e), session_methods=session_methods
                )
                await session_methods.session.commit()

    @staticmethod
    async def extend_with_key(message: Message):
        """
        Логика продления подписки с использованием нового ключа.

        Этот метод будет использоваться для продления подписки с использованием нового ключа доступа.
        Его реализация будет зависеть от требований системы.

        Args:
            callback (telegram.CallbackQuery): Запрос от Telegram с данными callback.
            callback_data (dict): Данные, переданные вместе с callback.
        """
        pass

    @staticmethod
    async def send_success_response(message: Message, vpn_key: str):
        """
        Отправляет пользователю успешное уведомление с VPN ключом.

        Args:
            message (telegram.Message): Сообщение от Telegram, в которое будет отправлено уведомление.
            vpn_key (str): Ключ доступа VPN, который будет отправлен пользователю.
        """
        await message.answer(
            text=f'<pre>{vpn_key}</pre>',
            parse_mode="HTML",
        )
        await message.answer(
            text='Выбери свое устройство ниже 👇 для того, чтобы я показал тебе простую инструкцию подключения🔌',
            reply_markup=await ReplyKeyboards.get_menu_install_app()
        )

    @staticmethod
    async def refund_payment(message: Message):
        """
        Обрабатывает возврат платежа через Telegram.

        Args:
            message (telegram.Message): Сообщение от Telegram, содержащее информацию о платеже.
        """
        await message.bot.refund_star_payment(message.from_user.id,
                                              message.successful_payment.telegram_payment_charge_id)
