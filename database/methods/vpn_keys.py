# database/methods/vpn_key_methods.py

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.models import VPNKeys


class VPNKeyMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_vpn_key(self, vpnkey: VPNKeys):
        result = await self.session.execute(select(VPNKeys).filter_by(id=vpnkey.id))
        existing_key = result.scalars().first()

        if existing_key:
            existing_key.issued_at = vpnkey.issued_at
            existing_key.is_active = vpnkey.is_active
            existing_key.is_blocked = vpnkey.is_blocked
            existing_key.updated_at = datetime.now()

            await self.session.commit()
            return True
        return False

    async def get_vpn_key(self):
        result = await self.session.execute(
            select(VPNKeys).filter_by(is_active=False, is_blocked=False)
        )
        vpn_key = result.scalars().first()
        return vpn_key
