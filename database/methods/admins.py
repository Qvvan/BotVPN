from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.models import Admins


class AdminMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def admin_exists(self, tg_id: int) -> bool:
        try:
            result = await self.session.execute(select(Admins).filter_by(tg_id=tg_id))
            user = result.scalars().first()
            return user is not None
        except SQLAlchemyError as e:
            print(f"Error checking if admin exists: {e}")
            return False

    async def add_admin(self, admins: Admins):
        try:
            if not await self.admin_exists(admins.tg_id):
                self.session.add(admins)
        except IntegrityError as e:
            print(f"Error adding admin: {e}")
        except SQLAlchemyError as e:
            print(f"Error adding admin: {e}")
