from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.models import VPNKeys


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
                existing_key.is_blocked = vpnkey.is_blocked
                existing_key.issued_at = datetime.now()
                existing_key.updated_at = datetime.now()

                self.session.add(existing_key)
                return True
            return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            print(f"Error updating VPN key: {e}")
            return False

    async def get_vpn_key(self):
        try:
            result = await self.session.execute(
                select(VPNKeys).filter_by(is_active=0, is_blocked=0)
            )
            vpn_key = result.scalars().first()
            return vpn_key
        except SQLAlchemyError as e:
            print(f"Error retrieving VPN key: {e}")
            return None

    async def add_vpn_key(self, key: str):
        try:
            self.session.add(VPNKeys(
                key=key,
            ))
        except Exception as err:
            return 'Не удалось добавить ключ', err

    async def get_keys(self):
        try:
            result = await self.session.execute(
                select(VPNKeys).filter_by(is_active=0, is_blocked=0)
            )
            vpn_key = result.scalars().all()
            return vpn_key
        except SQLAlchemyError as e:
            print(f"Error retrieving VPN key: {e}")
            return None
