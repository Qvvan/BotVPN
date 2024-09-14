from typing import Optional

from database.methods import GoogleSheetsMethods

class DB:
    __db: Optional[GoogleSheetsMethods] = None

    @staticmethod
    def set(methods: GoogleSheetsMethods):
        """Установить методы для работы с базой данных."""
        DB.__db = methods

    @staticmethod
    def get() -> GoogleSheetsMethods:
        """Получить методы для работы с базой данных."""
        if DB.__db is None:
            raise RuntimeError("DB.methods не инициализирован. Пожалуйста, вызовите DB.set() сначала.")
        return DB.__db
