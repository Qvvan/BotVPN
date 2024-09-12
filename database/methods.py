from pydantic import BaseModel


class GoogleSheetsMethods:
    def __init__(self, connection, spreadsheet_id: str):
        self.client = connection.client
        self.spreadsheet = self.client.open_by_key(spreadsheet_id)

    def user_exists(self, username: str) -> bool:
        """Проверить, существует ли пользователь с таким именем."""
        worksheet = self.spreadsheet.worksheet('Users')
        cell = worksheet.find(username)  # Ищем пользователя по имени
        return cell is not None

    def add_user(self, user: BaseModel):
        """Добавить нового пользователя в таблицу Users, если его нет в базе."""
        if self.user_exists(user.username):
            print(f"User {user.username} already exists.")
            return

        worksheet = self.spreadsheet.worksheet('Users')

        # Преобразуем данные модели пользователя в список значений
        user_data = [
            str(user.id),
            user.username,
            user.created_at.isoformat(),
            user.updated_at.isoformat()
        ]

        # Добавляем новую строку с данными пользователя
        worksheet.append_row(user_data, value_input_option='RAW')
        print(f"User {user.username} added successfully.")
