import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_data import config


class CustomLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        logging.basicConfig(
            format="%(levelname)s - %(asctime)s - %(name)s - %(filename)s - line: %(lineno)d - %(message)s",
            level=logging.INFO
        )

    async def notify_group(self, message: str, error: Exception = False):
        """Оповещение в соответствующую группу (ошибки или информация)."""
        group_id = config.ERROR_GROUP_ID if error else config.INFO_GROUP_ID
        notification_type = "🚨 Ошибка:\n" if error else "ℹ️ Информация:\n"

        async with Bot(
                token=config.BOT_TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        ) as bot:
            await bot.send_message(chat_id=group_id, text=f"{notification_type}{message}:{error}")

    async def log_info(self, message: str):
        """Логгирование информации и отправка уведомления."""
        self.logger.info(message)
        await self.notify_group(message)

    async def log_error(self, message: str, error: Exception):
        """Логгирование ошибки и отправка уведомления."""
        full_message = f"{message}. Error: {str(error)}"
        self.logger.error(full_message)
        await self.notify_group(message, error)


# Экземпляр логгера для использования в других модулях
logger = CustomLogger(__name__)
