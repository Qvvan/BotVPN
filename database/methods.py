from models.models import Transaction, VPNKey, Users


class GoogleSheetsMethods:
    def __init__(self, connection, spreadsheet_id: str):
        self.client = connection.client
        self.spreadsheet = self.client.open_by_key(spreadsheet_id)

    def user_exists(self, tg_id: str) -> bool:
        """Проверить, существует ли пользователь с таким именем."""
        worksheet = self.spreadsheet.worksheet('Users')
        cell = worksheet.find(tg_id)  # Ищем пользователя по имени
        return cell is not None

    def add_user(self, user: Users):
        """Добавить нового пользователя в таблицу Users, если его нет в базе."""
        if self.user_exists(str(user.tg_id)):

            return

        worksheet = self.spreadsheet.worksheet('Users')

        user_data = [
            str(user.tg_id),
            user.username,
            user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            user.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ]

        # Добавляем новую строку с данными пользователя
        worksheet.append_row(user_data, value_input_option='RAW')

    def get_services(self):
        """Получить все услуги из таблицы Service."""
        worksheet = self.spreadsheet.worksheet('Services')
        services = worksheet.get_all_records()
        return services

    def add_transaction(self, transaction: Transaction):
        worksheet = self.spreadsheet.worksheet('Transactions')

        transaction_data = [
            str(transaction.id),
            str(transaction.transaction_id),
            str(transaction.service_id),
            str(transaction.tg_id),
            transaction.status,
            transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            transaction.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ]

        worksheet.append_row(transaction_data, value_input_option='USER_ENTERED')
        return True

    @staticmethod
    def get_vpn_key(self, vpn: VPNKey):
        worksheet = self.spreadsheet.worksheet('VPNKeys')
        services = worksheet.get_all_records()
        return services
