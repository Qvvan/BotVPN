from sqlalchemy import update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logger.logging_config import logger
from models.models import Users


class UserMethods:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int):
        try:
            result = await self.session.execute(select(Users).filter_by(user_id=user_id))
            user = result.scalars().first()
            return user
        except SQLAlchemyError as e:
            await logger.log_error(f"Error checking if user exists", e)
            return False

    async def add_user(self, user: Users):
        try:
            if not await self.get_user(user.user_id):
                self.session.add(user)
                return True
            return False
        except IntegrityError as e:
            await logger.log_error(f"Error adding user", e)
        except SQLAlchemyError as e:
            await logger.log_error(f"Error adding user", e)

    async def ban_user(self, user_id: int):
        try:
            if await self.get_user(user_id):
                stmt = update(Users).where(Users.user_id == user_id).values(ban=1)
                await self.session.execute(stmt)
                return True

            return False
        except Exception as e:
            await logger.log_error(f"Error banning user", e)

    async def unban_user(self, user_id: int):
        try:
            if await self.get_user(user_id):
                stmt = update(Users).where(Users.user_id == user_id).values(ban=0)
                await self.session.execute(stmt)
                return True

            return False
        except Exception as e:
            await logger.log_error(f"Error unbanning user", e)

    async def get_paginated_users(self, page: int, limit: int):
        try:
            offset = (page - 1) * limit
            result = await self.session.execute(
                select(Users).offset(offset).limit(limit)
            )
            users = result.scalars().all()
            has_next = len(users) == limit
            return users, has_next
        except SQLAlchemyError as e:
            await logger.log_error("Error fetching paginated users", e)
            return [], False

    async def get_all_users(self):
        try:
            result = await self.session.execute(select(Users))
            users = result.scalars().all()
            return users
        except SQLAlchemyError as e:
            await logger.log_error("Error fetching all users", e)
            return False
