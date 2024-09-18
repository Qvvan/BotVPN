from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.models import Subscriptions


class SubscriptionMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_subscription(self, tg_id):
        try:
            result = await self.session.execute(select(Subscriptions).filter_by(tg_id=tg_id))
            subscription = result.scalars().first()
            return subscription is not None
        except SQLAlchemyError as e:
            print(f"Error retrieving subscription: {e}")
            return False

    async def create_sub(self, sub: Subscriptions):
        try:
            self.session.add(sub)
            return True
        except SQLAlchemyError as e:
            print(f"Error creating subscription: {e}")
            return False

    async def update_sub(self, sub: Subscriptions):
        try:
            result = await self.session.execute(select(Subscriptions).filter_by(tg_id=sub.tg_id))
            existing_sub = result.scalars().first()

            if not existing_sub:
                await self.create_sub(sub)
            else:
                existing_sub.service_id = sub.service_id
                existing_sub.vpn_key_id = sub.vpn_key_id
                existing_sub.start_date = sub.start_date
                existing_sub.end_date = sub.end_date
                existing_sub.updated_at = datetime.now()

                self.session.add(existing_sub)

            return True
        except SQLAlchemyError as e:
            print(f"Error updating subscription: {e}")
            return False
