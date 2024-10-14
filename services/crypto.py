from cryptography.fernet import Fernet

from config_data.config import CRYPTO_KEY

cipher = Fernet(CRYPTO_KEY)


def encrypt_part(data: str) -> str:
    """Зашифровывает данные."""
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data.decode('utf-8')


def decrypt_part(encrypted_data: str) -> str:
    """Дешифровывает данные."""
    decrypted_data = cipher.decrypt(encrypted_data.encode())
    return decrypted_data.decode('utf-8')
