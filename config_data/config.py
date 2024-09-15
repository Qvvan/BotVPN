import logging
from dataclasses import dataclass

from environs import Env

logger = logging.getLogger(__name__)

@dataclass
class TgBot:
    token: str
    admin_ids: list[int]

@dataclass
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str
    crypto_key: str


@dataclass
class Config:
    tg_bot: TgBot
    postgres: DatabaseConfig


def load_config(path: str | None = None) -> Config:
    """Загрузить конфигурацию из файла .env и вернуть объект Config."""
    env = Env()
    try:
        env.read_env(path)
        config = Config(
            tg_bot=TgBot(
                token=env('BOT_TOKEN'),
                admin_ids=list(map(int, env.list('ADMIN_IDS')))
            ),
            postgres=DatabaseConfig(
                host=env('DB_HOST'),
                port=env.int('DB_PORT'),
                name=env('DB_NAME'),
                user=env('DB_USER'),
                password=env('DB_PASSWORD'),
                crypto_key=env('CRYPTO_KEY')
            )
        )
        logger.info("Конфигурация успешно загружена.")
        return config
    except Exception as e:
        logger.error("Ошибка при загрузке конфигурации", exc_info=True)
        raise
