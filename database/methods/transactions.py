# database/methods/transaction_methods.py

import base64

from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.models import Transactions


class TransactionMethods:
    def __init__(self, session: AsyncSession, crypto_key: str):
        self.session = session
        self.cipher_suite = Fernet(crypto_key)

    async def add_transaction(self, transaction_code: str, service_id: int, user_id: int, status: str,
                              description: str) -> Transactions:
        transaction = Transactions(
            transaction_code=transaction_code,
            service_id=service_id,
            user_id=user_id,
            status=status,
            description=description,
        )

        encrypted_transaction_id = self.cipher_suite.encrypt(transaction_code.encode())
        transaction.transaction_code = base64.urlsafe_b64encode(encrypted_transaction_id).decode('utf-8')

        self.session.add(transaction)
        await self.session.commit()

        return transaction

    async def cancel_transaction(self, encrypted_transaction_code: str):
        decoded_data = base64.urlsafe_b64decode(encrypted_transaction_code)
        decrypted_transaction_id = self.cipher_suite.decrypt(decoded_data).decode('utf-8')

        result = await self.session.execute(
            select(Transactions).filter_by(transaction_code=encrypted_transaction_code)
        )
        transaction = result.scalars().first()

        if transaction:
            tg_id = transaction.user_id
            return tg_id, decrypted_transaction_id
        return None, None
