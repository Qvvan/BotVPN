from logger.logging_config import logger


class TransactionService:

    @staticmethod
    async def create_transaction(message, status, description, session_methods):
        try:
            in_payload = message.successful_payment.invoice_payload.split(':')
            transaction_code = message.successful_payment.telegram_payment_charge_id
            service_id = int(in_payload[0])
            user_id = message.from_user.id

            transaction = await session_methods.transactions.add_transaction(
                transaction_code=transaction_code,
                service_id=service_id,
                user_id=user_id,
                status=status,
                description=description,
            )
            return transaction
        except Exception as e:
            await logger.log_error(f"Пользователь: @{message.from_user.username}"
                                   f"Ошибка при создании транзакции", e)
            return None

    @staticmethod
    async def handle_failed_transaction(message, error_description):
        # Логика обработки неудачной транзакции
        pass
