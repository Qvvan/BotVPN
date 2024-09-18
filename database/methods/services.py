from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.models import Services


class ServiceMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_services(self):
        try:
            result = await self.session.execute(select(Services))
            services = result.scalars().all()
            return services
        except SQLAlchemyError as e:
            print(f"Error retrieving services: {e}")
            return []

    async def add_service(self, name: str, duration_days: int, price: int):
        service = Services(
            name=name,
            duration_days=duration_days,
            price=price
        )
        try:
            self.session.add(service)
            return service
        except SQLAlchemyError as e:
            print(f"Error adding service: {e}")
            return None
