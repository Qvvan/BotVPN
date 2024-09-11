from database.db_connect import GoogleSheetsConnection

class GoogleSheetsMethods:
    def __init__(self, connection: GoogleSheetsConnection, spreadsheet_id: str):
        self.connection = connection
        self.spreadsheet_id = spreadsheet_id
        self.sheet = self._get_spreadsheet()

    def _get_spreadsheet(self):
        return self.connection.client.open_by_key(self.spreadsheet_id)

    def create_sheet(self, title: str):
        # Создание нового листа
        spreadsheet = self.sheet
        spreadsheet.add_worksheet(title=title, rows="100", cols="20")
        return f"Sheet '{title}' created successfully."

    def add_column(self, sheet_name: str, column_name: str):
        # Добавление нового столбца
        worksheet = self.sheet.worksheet(sheet_name)
        col_num = len(worksheet.row_values(1)) + 1
        worksheet.update_cell(1, col_num, column_name)
        return f"Column '{column_name}' added to sheet '{sheet_name}'."
