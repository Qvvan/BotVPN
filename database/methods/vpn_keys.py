from datetime import datetime

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logger.logging_config import logger
from models.models import VPNKeys, Subscriptions, Users, Services


class VPNKeyMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_vpn_key(self, vpnkey: VPNKeys):
        try:
            result = await self.session.execute(select(VPNKeys).filter_by(vpn_key_id=vpnkey.vpn_key_id))
            existing_key = result.scalars().first()

            if existing_key:
                existing_key.issued_at = vpnkey.issued_at
                existing_key.is_active = vpnkey.is_active
                existing_key.issued_at = datetime.now()
                existing_key.updated_at = datetime.now()

                self.session.add(existing_key)
                return True
            return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error updating VPN key: {e}")
            return False

    async def get_vpn_key(self):
        try:
            result = await self.session.execute(
                select(VPNKeys).filter_by(is_active=0)
            )
            vpn_key = result.scalars().first()
            return vpn_key
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving VPN key: {e}")
            return None

    async def add_vpn_key(self, key: str, server_name: str, outline_key_id: str, server_id: str):
        try:
            self.session.add(VPNKeys(
                server_id=server_id,
                key=key,
                server_name=server_name,
                outline_key_id=outline_key_id,
            ))
        except Exception as e:
            logger.error(f"Error add VPN key: {e}")
            return None

    async def get_keys(self):
        try:
            result = await self.session.execute(
                select(VPNKeys).filter_by(is_active=0)
            )
            vpn_key = result.scalars().all()
            return vpn_key
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving VPN key: {e}")
            return None

    async def del_key(self, key_code: str):
        try:
            result = await self.session.execute(
                select(VPNKeys).filter_by(key=key_code)
            )
            vpn_key = result.scalar_one_or_none()

            if vpn_key is None:
                raise

            await self.session.delete(vpn_key)

            return True

        except SQLAlchemyError as e:
            logger.error('Не удалось удалить ключ', e)
            raise

    async def key_info(self, key_code: str):
        try:
            result = await self.session.execute(
                select(VPNKeys).filter_by(key=key_code)
            )
            vpn_key = result.scalar_one_or_none()
            if not vpn_key:
                raise Exception('Ключ не найден')
            # Если ключ используется (is_active = 1)
            if vpn_key.is_active == 1:
                subscription_result = await self.session.execute(
                    select(Subscriptions)
                    .filter_by(vpn_key_id=vpn_key.vpn_key_id)
                )
                subscription = subscription_result.scalar_one_or_none()

                if subscription:
                    user_result = await self.session.execute(
                        select(Users).filter_by(tg_id=subscription.user_id)
                    )
                    user = user_result.scalar_one_or_none()

                    service_result = await self.session.execute(
                        select(Services).filter_by(service_id=subscription.service_id)
                    )
                    service = service_result.scalar_one_or_none()

                    if user and service:
                        return {
                            "message": "Ключ используется",
                            "user_id": user.tg_id,
                            "username": user.username,
                            "start_date": subscription.start_date,
                            "end_date": subscription.end_date,
                            "last_update": vpn_key.updated_at,
                            "service_name": service.name
                        }

            # Если ключ не активен (is_active = 0)
            return {"message": "Ключем никто не пользуется"}

        except SQLAlchemyError as e:
            logger.error('Ошибка при получении информации о ключе', e)
            raise

    async def update_limit(self, vpn_key_id: int, new_limit: int):
        try:
            result = await self.session.execute(
                update(VPNKeys).
                where(VPNKeys.vpn_key_id == vpn_key_id).
                values(is_limit=new_limit)
            )

            if result.rowcount == 0:
                return False

            return True

        except SQLAlchemyError as e:
            logger.error(f'Ошибка при обновлении лимита для ключа {vpn_key_id}: {e}')
            await self.session.rollback()
            raise

    async def get_key_id(self, key_code: str):
        try:
            result = await self.session.execute(
                select(VPNKeys).filter_by(key=key_code)
            )
            vpn_key = result.scalar_one_or_none()

            if vpn_key is None:
                return False

            return vpn_key

        except SQLAlchemyError as e:
            logger.error('Не удалось удалить ключ', e)
            raise

    async def get_by_id(self, vpn_key_id: int):
        try:
            result = await self.session.execute(
                select(VPNKeys).filter_by(vpn_key_id=vpn_key_id)
            )
            vpn_key = result.scalar_one_or_none()

            if vpn_key is None:
                return False

            return vpn_key

        except SQLAlchemyError as e:
            logger.error('Не удалось удалить ключ', e)
            raise
