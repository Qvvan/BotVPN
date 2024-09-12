from typing import List

import gspread

from database.db_connect import GoogleSheetsConnection
from models.models import User, Service, Payment, VPNKey, Subscription, Log, Transaction


def create_sheet_if_not_exists(spreadsheet, sheet_name: str, columns: List[str]):
    """Создать новый лист, если он не существует."""
    try:
        spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=len(columns))
        worksheet.insert_row(columns, 1)
        print(f"Created sheet: {sheet_name} with columns: {columns}")


def update_sheet_if_necessary(worksheet, expected_columns: List[str]):
    """Обновить таблицу, если колонки изменились."""
    current_columns = worksheet.row_values(1)
    if set(current_columns) != set(expected_columns):
        # Удаляем старые столбцы, добавляем новые
        for col in current_columns:
            if col not in expected_columns:
                col_index = current_columns.index(col) + 1
                worksheet.delete_columns(col_index)
        # Добавляем новые столбцы
        for col in expected_columns:
            if col not in current_columns:
                worksheet.append_row([col], value_input_option='RAW')
        print(f"Updated sheet: {worksheet.title} to match columns: {expected_columns}")


def initialize_sheets(config):
    connection = GoogleSheetsConnection(config.google_sheets.credentials_file)
    spreadsheet = connection.client.open_by_key(config.google_sheets.spreadsheet_id)

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


def InitDB(config):
    # Инициализируем БД, создаем все таблицы если их нет, обновляем их при необходимости
    initialize_sheets(config)

    # Здесь можно вернуть необходимые методы, если нужно
    from database.methods import GoogleSheetsMethods
    connection = GoogleSheetsConnection(config.google_sheets.credentials_file)
    methods = GoogleSheetsMethods(connection, config.google_sheets.spreadsheet_id)
    return methods
