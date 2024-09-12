import logging
import os

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)


class GoogleSheetsConnection:
    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file
        if not os.path.isfile(self.credentials_file):
            logger.error(f"Файл учетных данных не найден: {self.credentials_file}")
            raise
        self.client = self._connect()

    def _connect(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        try:
            credentials = Credentials.from_service_account_file(self.credentials_file, scopes=scope)
            client = gspread.authorize(credentials)
            logger.info("Успешное подключение к Google Sheets")
            return client
        except ValueError as e:
            logger.error("Ошибка в формате файла учетных данных", exc_info=True)
            raise
        except Exception as e:
            logger.error("Ошибка при подключении к Google Sheets", exc_info=True)
            raise
