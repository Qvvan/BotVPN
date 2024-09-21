from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.models import Subscriptions, VPNKeys, Services


class SubscriptionMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_subscription(self, user_id):
        try:
            # Запрос с правильными join
            query = (
                select(
                    Subscriptions.start_date,
                    Subscriptions.end_date,
                    VPNKeys.key,
                    VPNKeys.server_name,
                    Services.name
                ).select_from(Subscriptions)
                .join(VPNKeys, Subscriptions.vpn_key_id == VPNKeys.vpn_key_id)
                .join(Services, Subscriptions.service_id == Services.service_id)
                .filter(Subscriptions.user_id == user_id)
            )

            result = await self.session.execute(query)
            subscription = result.fetchall()  # Получаем первую (и, надеюсь, единственную) запись
            if len(subscription) == 0:
                return None

            return subscription
        except SQLAlchemyError as e:
            print(f"Error retrieving subscription: {e}")
            return None

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

    async def create_sub(self, sub: Subscriptions):
        try:
            self.session.add(sub)
            return True
        except SQLAlchemyError as e:
            print(f"Error creating subscription: {e}")
            return False
