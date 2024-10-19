from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logger.logging_config import logger
from models.models import Subscriptions, Services


class SubscriptionMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_subscription(self, user_id):
        try:
            query = (
                select(
                    Subscriptions.start_date,
                    Subscriptions.end_date,
                    Subscriptions.dynamic_key,
                    Services.name,
                    Subscriptions.status,
                    Subscriptions.subscription_id,
                    Services.duration_days,
                    Services.price,
                    Services.service_id,
                ).select_from(Subscriptions)
                .join(Services, Subscriptions.service_id == Services.service_id)
                .filter(Subscriptions.user_id == user_id)
            )

            result = await self.session.execute(query)
            subscription = result.mappings().all()
            if len(subscription) == 0:
                return None

            return subscription
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving subscription: {e}")
            return None

    async def update_sub(self, sub: Subscriptions):
        try:
            result = await self.session.execute(select(Subscriptions).filter_by(
                user_id=sub.user_id,
                dynamic_key=sub.dynamic_key,
            ))
            existing_sub = result.scalars().first()

            if not existing_sub:
                await self.create_sub(sub)
            else:
                existing_sub.service_id = sub.service_id
                existing_sub.dynamic_key = sub.dynamic_key
                existing_sub.start_date = sub.start_date
                existing_sub.end_date = sub.end_date
                existing_sub.updated_at = datetime.now()
                existing_sub.status = sub.status
                existing_sub.reminder_sent = sub.reminder_sent

                self.session.add(existing_sub)

            return True
        except SQLAlchemyError as e:
            logger.error(f"Error updating subscription: {e}")
            raise

    async def create_sub(self, sub: Subscriptions):
        try:
            self.session.add(sub)
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error creating subscription: {e}")
            return False

    async def get_subs(self):
        try:
            result = await self.session.execute(
                select(Subscriptions)
            )
            subs = result.scalars().all()
            if len(subs) == 0:
                logger.info('Нет ни одной подписки')
                return False

            return subs
        except SQLAlchemyError as e:
            logger.error('Не удалось получить подписки', e)
            raise

    async def delete_sub(self, subscription_id: int):
        try:
            subscription = await self.session.get(Subscriptions, subscription_id)

            if subscription:
                await self.session.delete(subscription)
                return True
            return False

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении подписки с ID {subscription_id}: {e}")
            raise
