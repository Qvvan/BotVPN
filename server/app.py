from fastapi import FastAPI, HTTPException

from config_data.config import OUTLINE_SALT
from database.context_manager import DatabaseContextManager
from logger.logging_config import logger
from outline.outline_manager.outline_manager import OutlineManager
from services.crypto import decrypt_part

app = FastAPI()


@app.get('/access-key/{encrypted_part}')
async def get_key(encrypted_part: str):
    manager = OutlineManager()
    async with DatabaseContextManager() as session_methods:
        try:
            decrypted_key = decrypt_part(encrypted_part)

            decrypted_salt_and_user, server_id = decrypted_key.split("?server_id=")

            if not decrypted_salt_and_user.startswith(OUTLINE_SALT):
                raise ValueError("Invalid salt in the decrypted key")

            hex_id = decrypted_salt_and_user[len(OUTLINE_SALT):]
            user_id = str(int(hex_id, 16))

            sub = await session_methods.subscription.get_subscription(user_id)
            if sub:
                await manager.delete_key(server_id=server_id, key_id=user_id)

                new_key = await manager.create_key(server_id=server_id, user_id=user_id)
                decrypt_key = manager.decrypt_key(new_key)

                return decrypt_key
            return HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            logger.error('Произошла ошибка при получение ключа', e)
