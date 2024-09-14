from datetime import datetime

from models.models import Transaction, VPNKey, Users, Subscription


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

    def update_vpn_key(self, vpnkey: VPNKey):
        worksheet = self.spreadsheet.worksheet('VPNKeys')

        records = worksheet.get_all_records()
        for idx, record in enumerate(records):
            if record['id'] == vpnkey.id:
                row_index = idx + 2

                update_data = [
                    vpnkey.issued_at.strftime('%Y-%m-%d %H:%M:%S'),
                    vpnkey.is_active,
                    vpnkey.is_blocked,
                    vpnkey.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                ]

                worksheet.update(f'C{row_index}', [[update_data[0]]])
                worksheet.update(f'D{row_index}', [[update_data[1]]])
                worksheet.update(f'E{row_index}', [[update_data[2]]])
                worksheet.update(f'G{row_index}', [[update_data[3]]])

                return True

        return False

    def get_subscription(self, tg_id):
        """Проверить наличие подписки по tg_id в таблице Subscriptions."""
        worksheet = self.spreadsheet.worksheet('Subscriptions')
        subscriptions = worksheet.get_all_records()

        for subscription in subscriptions:
            if subscription.get('tg_id') == tg_id:
                return False

        return True

    def create_sub(self, sub: Subscription):
        worksheet = self.spreadsheet.worksheet('Subscriptions')

        subscription = [
            str(sub.id),
            str(sub.tg_id),
            str(sub.service_id),
            str(sub.vpn_key_id),
            sub.start_date.strftime('%Y-%m-%d %H:%M:%S'),
            sub.end_date.strftime('%Y-%m-%d %H:%M:%S'),
            sub.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            sub.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ]
        worksheet.append_row(subscription, value_input_option='RAW')
        return True

    from datetime import datetime

    def update_sub(self, sub: Subscription):
        worksheet = self.spreadsheet.worksheet('Subscriptions')

        if not self.get_subscription(sub.tg_id):
            self.create_sub(sub)
        else:
            subscriptions = worksheet.get_all_records()
            # Ищем строку с соответствующим tg_id
            for idx, record in enumerate(subscriptions):
                if record['tg_id'] == sub.tg_id:
                    # Найдена строка для обновления, получаем индекс
                    row_index = idx + 2  # Добавляем 2, чтобы учесть строку заголовков

                    # Подготавливаем данные для обновления
                    update_data = [
                        sub.tg_id,
                        str(sub.service_id),
                        str(sub.vpn_key_id),
                        sub.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                        sub.end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    ]

                    # Обновляем основные данные в строке
                    worksheet.update(f'B{row_index}:F{row_index}', [update_data])

                    # Отдельно обновляем поле updated_at
                    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    worksheet.update(f'H{row_index}', updated_at)

        return True
