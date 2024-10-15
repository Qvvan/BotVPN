from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.models import Subscription, Server


async def get_subscription(db: AsyncSession, user_id: int):
    """
    Получить подписку пользователя по его ID
    """
    result = await db.execute(select(Subscription).filter(Subscription.user_id == user_id))
    return result.scalars().first()


async def get_servers(db: AsyncSession):
    """
    Получить список всех серверов
    """
    result = await db.execute(select(Server))
    return result.scalars().all()
