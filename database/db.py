from typing import Optional
from database.postgres_methods import PostgresMethods

class DB:
    __db: Optional[PostgresMethods] = None

    @staticmethod
    def set(methods: PostgresMethods):
        """Установить методы для работы с базой данных."""
        DB.__db = methods

    @staticmethod
    def get() -> PostgresMethods:
        """Получить методы для работы с базой данных."""
        if DB.__db is None:
            raise RuntimeError("DB не инициализирован. Пожалуйста, вызовите DB.set() сначала.")
        return DB.__db
