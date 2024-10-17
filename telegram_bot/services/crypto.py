from cryptography.fernet import Fernet

from telegram_bot.config_data.config import CRYPTO_KEY

cipher = Fernet(CRYPTO_KEY)


def encrypt_part(data: str) -> str:
    """Зашифровывает данные."""
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data.decode('utf-8')



