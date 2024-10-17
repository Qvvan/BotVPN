from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from telegram_bot.config_data import config
from telegram_bot.logger.logging_config import logger


async def notify_group(message: str, is_error: bool = False):
    """Оповещение в соответствующую группу (ошибки или информация)."""
    group_id = config.ERROR_GROUP_ID if is_error else config.INFO_GROUP_ID
    notification_type = "🚨 Ошибка:\n" if is_error else "ℹ️ Информация:\n"

    async with Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    ) as bot:
        try:
            await bot.send_message(chat_id=group_id, text=f"{notification_type}{message}")
            logger.info(f"Notification sent to group {group_id}")
        except Exception as e:
            logger.error(f"Failed to send notification to group {group_id}: {e}")

