import base64
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from models.models import Transactions


class TransactionMethods:
    def __init__(self, session: Session, crypto_key: str):
        self.session = session
        self.cipher_suite = Fernet(crypto_key)

    def add_transaction(self, transaction: Transactions):
        # Шифрование transaction_id перед добавлением в базу данных
        encrypted_transaction_id = self.cipher_suite.encrypt(transaction.transaction_id.encode())
        transaction.transaction_id = base64.urlsafe_b64encode(encrypted_transaction_id).decode('utf-8')

        self.session.add(transaction)
        self.session.commit()
        return True

    def cancel_transaction(self, encrypted_transaction_id):
        # Декодируем из base64 и расшифровываем transaction_id
        decoded_data = base64.urlsafe_b64decode(encrypted_transaction_id)
        decrypted_transaction_id = self.cipher_suite.decrypt(decoded_data).decode('utf-8')

        transaction = self.session.query(Transactions).filter_by(transaction_id=encrypted_transaction_id).first()
        if transaction:
            tg_id = transaction.tg_id
            return tg_id, decrypted_transaction_id
        return None, None
