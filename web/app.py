import logging

from cryptography.fernet import Fernet
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from cfg.config import OUTLINE_SALT, CRYPTO_KEY
from db import methods
from db.database import get_db

cipher = Fernet(CRYPTO_KEY)

app = FastAPI()


async def decrypt_part(encrypted_data: str) -> str:
    """Дешифровывает данные."""
    decrypted_data = cipher.decrypt(encrypted_data.encode())
    return decrypted_data.decode('utf-8')


@app.get('/access-key/{encrypted_part}')
async def get_key(encrypted_part: str, db: Session = Depends(get_db)):
    try:
        decrypted_key = await decrypt_part(encrypted_part)

        if not decrypted_key.startswith(OUTLINE_SALT):
            return HTTPException(status_code=400, detail="Invalid requests")

        hex_id = decrypted_key[len(OUTLINE_SALT):]
        user_id = int(hex_id, 16)
    except Exception as e:
        logging.error("User not found:", e)
        return HTTPException(status_code=404, detail="User not found")

    sub = await methods.get_subscription(db, user_id)
    if not sub:
        return HTTPException(status_code=404, detail="User not found")

    servers = await methods.get_servers(db)
    return {"subscription": sub, "servers": servers}
