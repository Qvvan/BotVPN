import base64
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from models.models import Transactions


class TransactionMethods:
    def __init__(self, session: Session, crypto_key: str):
        self.session = session
        self.cipher_suite = Fernet(crypto_key)

    def add_transaction(self, transaction_code: str, service_id: int, user_id: int, status: str) -> Transactions:
        transaction = Transactions(
            transaction_code=transaction_code,
            service_id=service_id,
            user_id=user_id,
            status=status
        )

        encrypted_transaction_id = self.cipher_suite.encrypt(transaction_code.encode())
        transaction.transaction_code = base64.urlsafe_b64encode(encrypted_transaction_id).decode('utf-8')

        self.session.add(transaction)
        self.session.commit()

        return transaction

    def cancel_transaction(self, encrypted_transaction_code: str):
        decoded_data = base64.urlsafe_b64decode(encrypted_transaction_code)
        decrypted_transaction_id = self.cipher_suite.decrypt(decoded_data).decode('utf-8')

        transaction = self.session.query(Transactions).filter_by(transaction_code=encrypted_transaction_code).first()
        if transaction:
            tg_id = transaction.tg_id
            return tg_id, decrypted_transaction_id
        return None, None
