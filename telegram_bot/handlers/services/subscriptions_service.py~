import random
from datetime import datetime, timedelta

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.context_manager import DatabaseContextManager
from handlers.services.create_subscription_service import SubscriptionService
from handlers.services.create_transaction_service import TransactionService
from handlers.services.get_session_cookies import get_session_cookie
from handlers.services.key_create import ShadowsocksKeyManager, BaseKeyManager
from keyboards.kb_reply.kb_inline import ReplyKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from models.models import SubscriptionStatusEnum, StatusSubscriptionHistory


class NoAvailableServersError(Exception):
    pass


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
            shadowsocks_manager = None
            key_id = None
            error_message = None

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

                # Получение списка всех серверов с проверкой статуса hidden
                server_ips = await session_methods.servers.get_all_servers()
                available_servers = [server for server in server_ips if server.hidden == 0]

                # Перемешивание списка серверов
                random.shuffle(available_servers)

                # Перебор серверов, чтобы найти работающий
                server_ip = None
                session_cookie = None
                for server in available_servers:
                    try:
                        session_cookie = await get_session_cookie(server.server_ip)
                        if session_cookie:
                            server_ip = server.server_ip
                            break
                    except Exception as e:
                        await logger.error(f"Сервер {server.server_ip} не доступен", e)

                if not server_ip:
                    error_message = "На данный момент нет доступных серверов 😔. Мы уже сообщили в техподдержку, и скоро все исправим! Спасибо за ваше терпение 💙"
                    await logger.log_error(
                        message=f"Пользователь: @{message.from_user.username} попытался оформить подписку, но ни один сервер не ответил",
                        error="Не удалось получить сессию ни по одному из серверов"
                    )
                    raise NoAvailableServersError("нет доступных серверов")

                # Управление Shadowsocks ключами
                shadowsocks_manager = ShadowsocksKeyManager(server_ip, session_cookie)
                key, key_id = await shadowsocks_manager.manage_shadowsocks_key(
                    tg_id=str(user_id),
                    username=username,
                )

                # Создание подписки
                subscription_created = await SubscriptionService.create_subscription(
                    message, key, key_id, server_ip, session_methods
                )
                if not subscription_created:
                    raise Exception("Ошибка создания подписки")

                # Коммит сессии после успешных операций
                await session_methods.session.commit()
                await SubscriptionsService.send_success_response(message, key)
                await logger.log_info(f"Пользователь: @{message.from_user.username}\n"
                                      f"Оформил подписку на {duration_date} дней")

            except Exception as e:
                if isinstance(e, NoAvailableServersError):
                    # Сообщение уже отправлено пользователю, обработка завершена
                    await message.answer(text=error_message)
                else:
                    await logger.log_error(f"Пользователь: @{message.from_user.username}\n"
                                           f"Error during transaction processing", e)
                    await message.answer(text="К сожалению, покупка отменена.\nОбратитесь в техподдержку.")

                await SubscriptionsService.refund_payment(message)

                # Откат транзакции
                await session_methods.session.rollback()

                # Удаление ключа только если shadowsocks_manager и key_id существуют
                if shadowsocks_manager and key_id:
                    await shadowsocks_manager.delete_key(key_id)

                # Сохранение транзакции с отменой
                await TransactionService.create_transaction(
                    message, status='отмена', description=str(e), session_methods=session_methods
                )
                await session_methods.session.commit()

    @staticmethod
    async def extend_sub_successful_payment(message: Message, state: FSMContext):
        """
        Обрабатывает успешное продление подписки для пользователя.

        Args:
            message (Message): Сообщение от Telegram, содержащее информацию о платеже.
            state (FSMContext): Состояние для подписки, которую будем продлять.
        """
        async with DatabaseContextManager() as session_methods:
            try:
                in_payload = message.successful_payment.invoice_payload.split(':')
                durations_days = in_payload[1]
                user_data = await state.get_data()
                subscription_id = user_data.get('subscription_id')

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
                            if datetime.now() > sub.end_date:
                                new_end_date = datetime.now() + timedelta(days=int(durations_days))
                            else:
                                new_end_date = sub.end_date + timedelta(days=int(durations_days))
                            await session_methods.subscription.update_sub(
                                subscription_id=sub.subscription_id,
                                end_date=new_end_date,
                                updated_at=datetime.now(),
                                status=SubscriptionStatusEnum.ACTIVE,
                                reminder_sent=0
                            )
                            await session_methods.subscription_history.create_history_entry(
                                user_id=message.from_user.id,
                                service_id=sub.service_id,
                                start_date=sub.start_date,
                                end_date=new_end_date,
                                status=StatusSubscriptionHistory.EXTENSION
                            )
                            await message.answer(text=LEXICON_RU['subscription_renewed'])
                            session = await get_session_cookie(sub.server_ip)
                            await BaseKeyManager(server_ip=sub.server_ip, session_cookie=session).update_key_enable(sub.key_id,
                                                                                                             True)
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
