from cfg.config import DSN
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

async_engine = create_async_engine(DSN)

Session = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)


async def get_db():
    async with Session() as db:
        try:
            yield db
        finally:
            await db.close()
