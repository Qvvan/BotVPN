from models.models import VPNKey


class VPNKeyMethods:
    def __init__(self, spreadsheet):
        self.spreadsheet = spreadsheet

    def update_vpn_key(self, vpnkey: VPNKey):
        worksheet = self.spreadsheet.worksheet('VPNKeys')
        records = worksheet.get_all_records()

        for idx, record in enumerate(records):
            if str(record['id']) == vpnkey.id:
                row_index = idx + 2

                update_data = [
                    vpnkey.issued_at.strftime('%Y-%m-%d %H:%M:%S'),
                    vpnkey.is_active,
                    vpnkey.is_blocked,
                    vpnkey.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    vpnkey.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                ]

                worksheet.update(f'C{row_index}', [[update_data[0]]])
                worksheet.update(f'D{row_index}', [[update_data[1]]])
                worksheet.update(f'E{row_index}', [[update_data[2]]])
                worksheet.update(f'F{row_index}', [[update_data[3]]])
                worksheet.update(f'G{row_index}', [[update_data[4]]])
                return True
        return False

    def get_vpn_key(self):
        worksheet = self.spreadsheet.worksheet('VPNKeys')
        records = worksheet.get_all_records()

        for record in records:
            if record.get('is_active') == 0 and record.get('is_blocked') == 0:
                return record
        return None
