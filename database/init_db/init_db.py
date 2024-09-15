import asyncpg
import logging
from database.main_db import PostgresMethods
from database.db import DB

logger = logging.getLogger(__name__)


class InitDB:
    def __init__(self, config):
        self.config = config
        self.connection = None

    async def connect(self):
        try:
            # Подключаемся к базе данных
            self.connection = await asyncpg.connect(
                host=self.config.database.host,
                port=self.config.database.port,
                database=self.config.database.name,
                user=self.config.database.user,
                password=self.config.database.password
            )
            logger.info("Успешное подключение к базе данных PostgreSQL.")

            # Инициализируем методы работы с базой данных и устанавливаем их в статическом классе DB
            methods = PostgresMethods(self.connection)
            DB.set(methods)

        except Exception as e:
            logger.error("Ошибка при подключении к базе данных PostgreSQL.", exc_info=True)
            raise

    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("Соединение с базой данных закрыто.")
