from dataclasses import dataclass

from environs import Env


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
    env = Env()
    env.read_env(path)
    print(env('BOT_TOKEN'))
    return Config(
        tg_bot=TgBot(token=env('BOT_TOKEN')),
        google_sheets=GoogleSheetsConfig(
            credentials_file=env('GOOGLE_SHEETS_CREDENTIALS_FILE'),
            spreadsheet_id=env('SPREADSHEET_ID')  # Загружаем конфигурацию для Google Sheets
        )
    )
