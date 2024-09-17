# database/methods/service_methods.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.models import Services


class ServiceMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_services(self):
        result = await self.session.execute(select(Services))
        services = result.scalars().all()
        return services

    async def add_service(self, name: str, duration_days: int, price: int):
        new_service = Services(
            name=name,
            duration_days=duration_days,
            price=price
        )
        self.session.add(new_service)
        await self.session.commit()
        return new_service
