import logging
import psycopg2
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class PostgreSQLConnection:
    def __init__(self, db_name: str, user: str, password: str, host: str, port: int = 5432):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    @contextmanager
    def get_connection(self):
        try:
            conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            logger.info("Успешное подключение к базе данных PostgreSQL")
            yield conn
        except psycopg2.DatabaseError as e:
            logger.error("Ошибка при подключении к базе данных PostgreSQL", exc_info=True)
            raise
        finally:
            if conn:
                conn.close()
