import logging
from typing import List

import gspread

from database.db_connect import GoogleSheetsConnection
from models.models import User, Service, Payment, VPNKey, Subscription, Log, Transaction

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


def update_sheet_if_necessary(worksheet, expected_columns: List[str]):
    """Обновить таблицу, если колонки изменились."""
    current_columns = worksheet.row_values(1)
    if set(current_columns) != set(expected_columns):
        logger.info(f"Обновление листа: {worksheet.title} для соответствия колонкам: {expected_columns}")

        # Удаляем старые столбцы, добавляем новые
        for col in current_columns:
            if col not in expected_columns:
                col_index = current_columns.index(col) + 1
                worksheet.delete_columns(col_index)
        # Добавляем новые столбцы
        for col in expected_columns:
            if col not in current_columns:
                worksheet.append_row([col], value_input_option='RAW')

        logger.info(f"Обновлен лист: {worksheet.title} для соответствия колонкам: {expected_columns}")


def initialize_sheets(config):
    """Инициализировать листы в Google Sheets."""
    try:
        connection = GoogleSheetsConnection(config.google_sheets.credentials_file)
        spreadsheet = connection.client.open_by_key(config.google_sheets.spreadsheet_id)
    except Exception as e:
        logger.error("Ошибка при установлении соединения с Google Sheets", exc_info=True)
        raise

    # Определяем модели для каждой таблицы
    sheets = {
        'Users': User,
        'Services': Service,
        'Payments': Payment,
        'VPNKeys': VPNKey,
        'Subscriptions': Subscription,
        'Logs': Log,
        'Transactions': Transaction,
    }

    # Создаем и обновляем таблицы
    for sheet_name, model in sheets.items():
        expected_columns = list(model.__fields__.keys())
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            update_sheet_if_necessary(worksheet, expected_columns)
        except gspread.exceptions.WorksheetNotFound:
            create_sheet_if_not_exists(spreadsheet, sheet_name, expected_columns)
        except Exception as e:
            logger.error(f"Ошибка при работе с листом: {sheet_name}", exc_info=True)


def InitDB(config):
    """Инициализировать БД, создать все таблицы если их нет, обновить их при необходимости."""
    try:
        initialize_sheets(config)
        from database.methods import GoogleSheetsMethods
        connection = GoogleSheetsConnection(config.google_sheets.credentials_file)
        methods = GoogleSheetsMethods(connection, config.google_sheets.spreadsheet_id)
        return methods
    except Exception as e:
        logger.error("Ошибка при инициализации базы данных", exc_info=True)
        raise
