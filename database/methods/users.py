# database/methods/user_methods.py

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.models import Users


class UserMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def user_exists(self, tg_id: str) -> bool:
        result = await self.session.execute(select(Users).filter_by(tg_id=tg_id))
        user = result.scalars().first()
        return user is not None

    async def add_user(self, user: Users):
        if await self.user_exists(user.tg_id):
            return
        try:
            self.session.add(user)
        except IntegrityError as e:
            await self.session.rollback()
            # Replace print with proper logging if needed
            print(f"Error adding user: {e}")
