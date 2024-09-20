from environs import Env
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from models.models import Base

env = Env()

class DataBase:
    def __init__(self):
        self.host = env.str('DB_HOST')
        self.port = env.int('DB_PORT')
        self.user = env.str('DB_USER')
        self.password = env.str('DB_PASSWORD')
        self.db_name = env.str('DB_NAME')
        self.crypto_key = env.str('CRYPTO_KEY')

        self.connect = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"

        self.async_engine = create_async_engine(self.connect)
        self.Session = async_sessionmaker(bind=self.async_engine, class_=AsyncSession)

    async def create_db(self):
        async with self.async_engine.begin() as connect:
            await connect.run_sync(Base.metadata.create_all)
