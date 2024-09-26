from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logger.logging_config import logger
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
            logger.error(f"Ошибка получение услуги: {e}")
            return []


    async def get_service_by_id(self, service_id: int):
        try:
            result = await self.session.execute(
                select(Services).filter_by(service_id=service_id)
            )
            service = result.scalar_one_or_none()

            if service is None:
                return False

            return service
        except Exception as e:
            logger.error('Не удалось взять данную услугу', e)
            raise

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
            logger.error(f"Error adding service: {e}")
            return None
