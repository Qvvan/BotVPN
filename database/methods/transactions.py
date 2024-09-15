import base64

from cryptography.fernet import Fernet

from models.models import Transaction


class TransactionMethods:
    def __init__(self, spreadsheet, crypto_key):
        self.spreadsheet = spreadsheet
        self.cipher_suite = Fernet(crypto_key)

    def add_transaction(self, transaction: Transaction):
        worksheet = self.spreadsheet.worksheet('Transactions')

        encrypted_transaction_id = self.cipher_suite.encrypt(transaction.transaction_id.encode())
        encrypted_str = base64.urlsafe_b64encode(encrypted_transaction_id).decode('utf-8')

        transaction_data = [
            encrypted_str,
            transaction.service_id,
            transaction.tg_id,
            transaction.status,
            transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            transaction.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ]

        worksheet.append_row(transaction_data, value_input_option='USER_ENTERED')
        return True

    def cancel_transaction(self, encrypted_transaction_id):
        worksheet = self.spreadsheet.worksheet('Transactions')

        cell = worksheet.find(encrypted_transaction_id)
        if cell:
            decrypted_data = self.cipher_suite.decrypt(encrypted_transaction_id).decode('utf-8')
            row = worksheet.row_values(cell.row)
            tg_id = row[2]
            return tg_id, decrypted_data

        return None, None
