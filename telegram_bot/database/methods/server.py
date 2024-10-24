from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logger.logging_config import logger
from models.models import Servers


class ServerMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def server_exists(self, api_url: str) -> bool:
        """
        Проверяет, существует ли сервер с данным api_url в базе данных.
        """
        try:
            result = await self.session.execute(select(Servers).filter_by(api_url=api_url))
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
            server_id = server_data.get("SERVER_ID")
            name = server_data.get("NAME")
            api_url = server_data.get("API_URL")
            cert_sha256 = server_data.get("CERT_SHA256")

            if not await self.server_exists(api_url):
                new_server = Servers(
                    server_id=server_id,
                    name=name,
                    api_url=api_url,
                    cert_sha256=cert_sha256
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
