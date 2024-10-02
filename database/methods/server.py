from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logger.logging_config import logger
from models.models import Servers, VPNKeys, Subscriptions


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
            logger.error(f"Error checking if server exists: {e}")
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
                logger.error(f"Server with api_url '{api_url}' already exists.")
                return False

        except IntegrityError as e:
            await self.session.rollback()  # Откатываем транзакцию в случае ошибки
            logger.error(f"Integrity error when adding server: {e}")
            return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"SQLAlchemy error when adding server: {e}")
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
            logger.error(f"Error fetching servers from the database: {e}")
            return []

    async def get_server_by_vpn_key_id(self, vpn_key_id: str):
        try:
            result = await self.session.execute(
                select(
                    VPNKeys.server_id,
                    VPNKeys.outline_key_id
                ).select_from(
                    Subscriptions
                ).join(
                    VPNKeys, VPNKeys.vpn_key_id == Subscriptions.vpn_key_id
                ).filter(VPNKeys.vpn_key_id == vpn_key_id)
            )

            result = result.fetchone()

            if result is None:
                return False

            return result
        except Exception as e:
            logger.error('Ошибка при получении сервера по айди vpn key', e)
            return False
