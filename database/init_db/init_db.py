from database.db_connect import GoogleSheetsConnection
from database.methods import GoogleSheetsMethods


def InitDB(config):
    connection = GoogleSheetsConnection(config.google_sheets.credentials_file)
    methods = GoogleSheetsMethods(connection, config.google_sheets.spreadsheet_id)
    return methods
