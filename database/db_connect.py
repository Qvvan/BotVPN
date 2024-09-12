import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetsConnection:
    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file
        self.client = self._connect()

    def _connect(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_file(self.credentials_file, scopes=scope)
        client = gspread.authorize(credentials)
        return client
