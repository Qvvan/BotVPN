from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.db import DB
from database.postgres_methods import PostgresMethods
from models.models import Base

engine = None


def init_db(config):
    global engine

    # Создаем движок базы данных (соединение)
    engine = create_engine(config.database.database_url)

    # Создаем таблицы, если они еще не существуют
    Base.metadata.create_all(bind=engine)

    # Создаем sessionmaker, который будет использоваться для создания сессий
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Создаем экземпляр сессии
    session = SessionLocal()

    # Создаем экземпляр PostgresMethods и устанавливаем его
    postgres_methods = PostgresMethods(session, config.database.crypto_key)
    DB.set(postgres_methods)

class DataBase():
    def __init__(self, cfg):
        self.connect = cfg.database.database_url
        self.async_engine = create_async_engine(self.connect)
        self.Session = async_sessionmaker(bind=self.async_engine, class_=AsyncSession)

    async def create_db(self):
        async with self.async_engine.begin() as connect:
            await connect.run_sync(Base.metadata.create_all)