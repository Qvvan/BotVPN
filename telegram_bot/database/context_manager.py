from sqlalchemy import text

from telegram_bot.database.db_methods import MethodsManager
from telegram_bot.database.init_db import DataBase


class DatabaseContextManager:
    def __init__(self):
        self.db = DataBase()
        self.session = None
        self.methods = None

    async def __aenter__(self):
        self.session = self.db.Session()

        async with self.session.begin():
            await self.session.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;"))

        self.methods = MethodsManager(self.session)
        return self.methods

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
