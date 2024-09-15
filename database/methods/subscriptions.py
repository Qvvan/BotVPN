from models.models import Subscription
from datetime import datetime


class SubscriptionMethods:
    def __init__(self, spreadsheet):
        self.spreadsheet = spreadsheet

    def get_subscription(self, tg_id):
        worksheet = self.spreadsheet.worksheet('Subscriptions')
        subscriptions = worksheet.get_all_records()

        for subscription in subscriptions:
            if subscription.get('tg_id') == tg_id:
                return False
        return True

    def create_sub(self, sub: Subscription):
        worksheet = self.spreadsheet.worksheet('Subscriptions')

        subscription = [
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

    def update_sub(self, sub: Subscription):
        worksheet = self.spreadsheet.worksheet('Subscriptions')

        if not self.get_subscription(sub.tg_id):
            self.create_sub(sub)
        else:
            subscriptions = worksheet.get_all_records()
            for idx, record in enumerate(subscriptions):
                if record['tg_id'] == sub.tg_id:
                    row_index = idx + 2

                    update_data = [
                        sub.tg_id,
                        str(sub.service_id),
                        str(sub.vpn_key_id),
                        sub.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                        sub.end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    ]

                    worksheet.update(f'A{row_index}:E{row_index}', [update_data])
                    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    worksheet.update(f'G{row_index}', updated_at)

        return True
