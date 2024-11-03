from sqlalchemy import update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logger.logging_config import logger
from models.models import Servers


class ServerMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def server_exists(self, server_ip: str) -> bool:
        """
        Проверяет, существует ли сервер с данным api_url в базе данных.
        """
        try:
            result = await self.session.execute(select(Servers).filter_by(server_ip=server_ip))
            server = result.scalars().first()
            return server is not None
        except SQLAlchemyError as e:
            await logger.log_error(f"Error checking if server exists", e)
            return False

    async def add_server(self, server_data: dict) -> bool:
        """
        Добавляет сервер в базу данных, если его еще нет.
        """
        try:
            server_ip = server_data.get("SERVER_IP")
            name = server_data.get("NAME")
            limit = server_data.get("LIMIT")

            if not await self.server_exists(server_ip):
                new_server = Servers(
                    server_ip=server_ip,
                    name=name,
                    limit=limit
                )
                self.session.add(new_server)

                await self.session.commit()
                return True
            else:
                return False

        except IntegrityError as e:
            await self.session.rollback()
            await logger.log_error(f"Integrity error when adding server", e)
            return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            await logger.log_error(f"SQLAlchemy error when adding server", e)
            return False

    async def get_all_servers(self):
        """
        Получает список всех серверов из базы данных.
        """
        try:
            result = await self.session.execute(select(Servers))
            servers = result.scalars().all()
            return servers
        except SQLAlchemyError as e:
            await logger.log_error(f"Error fetching servers from the database", e)
            return []

    async def update_server(self, server_ip, **kwargs):
        """
        Универсальное обновление сервера в базе данных.
        server_ip: str - IP адрес сервера, который необходимо обновить
        kwargs: dict - поля для обновления и их значения
        """
        try:
            await self.session.execute(
                update(Servers).where(Servers.server_ip == server_ip).values(**kwargs)
            )
            await self.session.commit()
        except SQLAlchemyError as e:
            await logger.log_error(f"Error updating server {server_ip}", e)
            raise
