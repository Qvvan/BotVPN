from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from logger.logging_config import logger
from models.models import SubscriptionsHistory


class SubscriptionsHistoryMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_history_entry(self, user_id, service_id, start_date, end_date, status):
        """
        Creates a record in the subscriptions history table.

        Args:
            user_id (int): ID of the user.
            service_id (int): Service ID related to the subscription.
            start_date (datetime): Start date of the subscription period.
            end_date (datetime): End date of the subscription period.
            status (str): Статус подписки, продление или новая подписка.
        """
        try:
            history_entry = SubscriptionsHistory(
                user_id=user_id,
                service_id=service_id,
                start_date=start_date,
                end_date=end_date,
                status=status,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(history_entry)
        except Exception as e:
            await logger.log_error(f"Error creating history entry for user {user_id}", e)
            raise
