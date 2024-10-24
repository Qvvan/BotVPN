from datetime import datetime, timedelta

from logger.logging_config import logger
from models.models import Subscriptions


class SubscriptionService:

    @staticmethod
    async def create_subscription(message, dynamic_key: str, session_methods) -> bool:
        try:
            in_payload = message.successful_payment.invoice_payload.split(':')
            service_id = int(in_payload[0])
            durations_days = in_payload[1]

            subscription = await session_methods.subscription.create_sub(
                Subscriptions(
                    user_id=message.from_user.id,
                    service_id=service_id,
                    dynamic_key=dynamic_key,
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=int(durations_days)),
                )
            )

            return subscription is not None
        except Exception as e:
            logger.log_error(f"Пользователь: @{message.from_user.username}" 
                             f"Ошибка при создании подписки", e)
            return False
