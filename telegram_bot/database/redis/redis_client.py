import redis
from telegram_bot.config_data.config import REDIS_HOST, REDIS_PORT, REDIS_DB
from telegram_bot.logger.logging_config import logger


class RedisClient:
    def __init__(self):
        self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    def add_dynamic_key(self, dynamic_key: str, static_key: str) -> None:
        """Добавляет динамический ключ в формате dynamic_key:static_key"""
        key = f"{dynamic_key}:{static_key}"
        self.client.set(key, static_key)
        logger.info(f"Добавлен ключ: {key}")

    def delete_dynamic_key(self, dynamic_key: str, static_key: str) -> None:
        """Удаляет динамический ключ в формате dynamic_key:static_key"""
        key = f"{dynamic_key}:{static_key}"
        self.client.delete(key)
        logger.info(f"Удален ключ: {key}")
