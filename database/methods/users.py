from models.models import Users


class UserMethods:
    def __init__(self, spreadsheet):
        self.spreadsheet = spreadsheet

    def user_exists(self, tg_id: str) -> bool:
        worksheet = self.spreadsheet.worksheet('Users')
        cell = worksheet.find(tg_id)
        return cell is not None

    def add_user(self, user: Users):
        if self.user_exists(str(user.tg_id)):
            return

        worksheet = self.spreadsheet.worksheet('Users')

        user_data = [
            str(user.tg_id),
            user.username,
            user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ]

        worksheet.append_row(user_data, value_input_option='RAW')
