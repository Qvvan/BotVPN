from sqlalchemy import create_engine
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
