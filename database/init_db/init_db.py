from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.postgres_methods import PostgresMethods
from database.db import DB
from models.models import Base

# Глобальные переменные для хранения engine и sessionmaker
engine = None
SessionLocal = None


def init_db(config):
    global engine, SessionLocal

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

    # Возвращаем объект sessionmaker для дальнейшего использования
    return SessionLocal


# Функция для получения новой сессии в других частях проекта
def get_session():
    if SessionLocal is None:
        raise RuntimeError("База данных не инициализирована. Сначала вызовите init_db().")
    return SessionLocal()
