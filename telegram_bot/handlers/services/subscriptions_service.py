from datetime import datetime, timedelta

from aiogram.types import Message

from config_data.config import OUTLINE_SALT
from config_data.config import OUTLINE_USERS_GATEWAY
from database.context_manager import DatabaseContextManager
from handlers.services.create_subscription_service import SubscriptionService
from handlers.services.create_transaction_service import TransactionService
from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from models.models import Subscriptions, SubscriptionStatusEnum
from utils.crypto import encrypt_part


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

                # Создание транзакции
                transaction_state = await TransactionService.create_transaction(
                    message, 'successful', 'successful', session_methods
                )
                if not transaction_state:
                    raise Exception("Ошибка сохранения транзакции")

                # Генерация динамического ключа для VPN
                part_to_encrypt = f"{OUTLINE_SALT}{hex(int(user_id))[2:]}"
                encrypted_part = encrypt_part(part_to_encrypt)
                dynamic_key = f"{OUTLINE_USERS_GATEWAY}/access-key/{encrypted_part}#VPN"

                # Создание подписки
                subscription_created = await SubscriptionService.create_subscription(
                    message, dynamic_key, session_methods
                )
                if not subscription_created:
                    raise Exception("Ошибка создания подписки")

                await session_methods.session.commit()
                await SubscriptionsService.send_success_response(message, dynamic_key)
                logger.log_info(f"Пользователь: @{message.from_user.username}\n"
                                f"Оформил подписку на {duration_date} дней")

            except Exception as e:
                logger.log_error(f"Пользователь: @{message.from_user.username}\n"
                                 f"Error during transaction processing", e)
                await message.answer(text="К сожалению, покупка отменена.\nОбратитесь в техподдержку.")
                await SubscriptionsService.refund_payment(message)

                # Откат транзакции
                await session_methods.session.rollback()

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
                            await session_methods.subscription.update_sub(Subscriptions(
                                user_id=message.from_user.id,
                                service_id=service_id,
                                dynamic_key=sub.dynamic_key,
                                start_date=datetime.now(),
                                end_date=datetime.now() + timedelta(days=int(durations_days)),
                                updated_at=datetime.now(),
                                status=SubscriptionStatusEnum.ACTIVE,
                            ))
                            await message.answer(text=LEXICON_RU['subscription_renewed'])
                            await session_methods.session.commit()
                            logger.log_info(f"Пользователь: @{message.from_user.username}\n"
                                            f"Продлил подписку на {durations_days} дней")
                else:
                    await message.answer(text="Подписка не найдена. Проверьте данные.")

            except Exception as e:
                logger.log_error(f"Пользователь: @{message.from_user.username}\n"
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
            text='Ты успешно оформил подписку. ✅ Держи инструкцию по установке Outline и ключа ⬇️',
            reply_markup=await InlineKeyboards.get_guide()
        )
        await message.answer(
            text=f'<pre>{vpn_key}</pre>',
            parse_mode="HTML",
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
