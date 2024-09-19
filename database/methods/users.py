from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.models import Users


class UserMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def user_exists(self, tg_id: int) -> bool:
        try:
            result = await self.session.execute(select(Users).filter_by(tg_id=tg_id))
            user = result.scalars().first()
            return user is not None
        except SQLAlchemyError as e:
            print(f"Error checking if user exists: {e}")
            return False

    async def add_user(self, user: Users):
        try:
            if not await self.user_exists(user.tg_id):
                self.session.add(user)
        except IntegrityError as e:
            print(f"Error adding user: {e}")
        except SQLAlchemyError as e:
            print(f"Error adding user: {e}")