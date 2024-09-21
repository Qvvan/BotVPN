from logger.logging_config import logger
from dataclasses import dataclass

from environs import Env

env = Env()
env.read_env()


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]


@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    db_name: str
    crypto_key: str

    @property
    def database_url(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


@dataclass
class Config:
    tg_bot: TgBot
    database: DatabaseConfig


ADMIN_IDS = [int(admin) for admin in env.list('ADMIN_IDS')]


def load_config(path: str | None = None) -> Config:
    """Загрузить конфигурацию из файла .env и вернуть объект Config."""
    try:
        env.read_env(path)
        config = Config(
            tg_bot=TgBot(
                token=env('BOT_TOKEN'),
                admin_ids=list(map(int, env.list('ADMIN_IDS')))
            ),
            database=DatabaseConfig(
                host=env.str('DB_HOST'),
                port=env.int('DB_PORT'),
                user=env.str('DB_USER'),
                password=env.str('DB_PASSWORD'),
                db_name=env.str('DB_NAME'),
                crypto_key=env.str('CRYPTO_KEY')
            )
        )
        logger.info("Конфигурация успешно загружена.")
        return config
    except Exception as e:
        logger.error("Ошибка при загрузке конфигурации", exc_info=True)
        raise
