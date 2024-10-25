from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Pushes


class PushesMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_push_record(self, message: str, user_ids: list[int]):
        """Добавление записи о рассылке."""
        stmt = insert(Pushes).values(message=message, user_ids=user_ids)
        await self.session.execute(stmt)
        await self.session.commit()
