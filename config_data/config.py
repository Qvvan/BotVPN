import logging
from dataclasses import dataclass

from environs import Env

logger = logging.getLogger(__name__)

@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту


@dataclass
class GoogleSheetsConfig:
    credentials_file: str
    spreadsheet_id: str


@dataclass
class Config:
    tg_bot: TgBot
    google_sheets: GoogleSheetsConfig


def load_config(path: str | None = None) -> Config:
    """Загрузить конфигурацию из файла .env и вернуть объект Config."""
    env = Env()
    try:
        env.read_env(path)
        config = Config(
            tg_bot=TgBot(token=env('BOT_TOKEN')),
            google_sheets=GoogleSheetsConfig(
                credentials_file=env('GOOGLE_SHEETS_CREDENTIALS_FILE'),
                spreadsheet_id=env('SPREADSHEET_ID')  # Загружаем конфигурацию для Google Sheets
            )
        )
        logger.info("Конфигурация успешно загружена.")
        return config
    except Exception as e:
        logger.error("Ошибка при загрузке конфигурации", exc_info=True)
        raise
