import logging
from typing import List

import gspread

from database.db import DB
from database.init_db.db_connect import GoogleSheetsConnection
from database.main_db import GoogleSheetsMethods
from models.models import Users, Service, VPNKey, Subscription, Log, Transaction

logger = logging.getLogger(__name__)


def create_sheet_if_not_exists(spreadsheet, sheet_name: str, columns: List[str]):
    """Создать новый лист, если он не существует."""
    try:
        spreadsheet.worksheet(sheet_name)
        logger.info(f"Лист уже существует: {sheet_name}")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=len(columns))
        worksheet.insert_row(columns, 1)
        logger.info(f"Создан лист: {sheet_name} с колонками: {columns}")


def initialize_sheets(config, connection):
    """Инициализировать листы в Google Sheets."""
    try:
        spreadsheet = connection.client.open_by_key(config.google_sheets.spreadsheet_id)
    except Exception as e:
        logger.error("Ошибка при установлении соединения с Google Sheets", exc_info=True)
        raise

    sheets = {
        'Users': Users,
        'Services': Service,
        'VPNKeys': VPNKey,
        'Subscriptions': Subscription,
        'Logs': Log,
        'Transactions': Transaction,
    }

    for sheet_name, model in sheets.items():
        expected_columns = list(model.__fields__.keys())
        try:
            create_sheet_if_not_exists(spreadsheet, sheet_name, expected_columns)
        except Exception as e:
            logger.error(f"Ошибка при работе с листом: {sheet_name}", exc_info=True)


def InitDB(config):
    """Инициализировать БД, создать все таблицы если их нет."""
    try:
        connection = GoogleSheetsConnection(config.google_sheets.credentials_file)
        initialize_sheets(config, connection)
        method = GoogleSheetsMethods(connection, config.google_sheets.spreadsheet_id, config.google_sheets.crypto_key)
        DB.set(method)
    except Exception as e:
        logger.error("Ошибка при инициализации базы данных", exc_info=True)
        raise
