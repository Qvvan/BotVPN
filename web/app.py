import asyncio
import logging
from cryptography.fernet import Fernet
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from cfg.config import OUTLINE_SALT, CRYPTO_KEY
from db import methods
from db.database import get_db

cipher = Fernet(CRYPTO_KEY)
app = FastAPI()

# Словарь для хранения активных IP и времени их добавления
active_ips = {}

async def decrypt_part(encrypted_data: str) -> str:
    """Дешифровывает данные."""
    decrypted_data = cipher.decrypt(encrypted_data.encode())
    return decrypted_data.decode('utf-8')

async def manage_active_ips():
    """Удаляет IP-адреса, которые были активны больше 5 секунд назад."""
    while True:
        await asyncio.sleep(1)
        current_time = asyncio.get_event_loop().time()

        to_remove = [ip for ip, timestamp in active_ips.items() if current_time - timestamp > 5]
        for ip in to_remove:
            del active_ips[ip]
            logging.info(f"Removed inactive IP: {ip}")

@app.on_event("startup")
async def startup_event():
    """Запускает корутину для управления активными IP-адресами при старте приложения."""
    asyncio.create_task(manage_active_ips())

@app.get('/access-key/{encrypted_part}')
async def get_key(encrypted_part: str, request: Request, db: Session = Depends(get_db)):
    user_ip = request.client.host
    current_time = asyncio.get_event_loop().time()  # Используем время цикла событий

    # Добавляем IP в активные с текущим временем
    active_ips[user_ip] = current_time
    logging.info(f"Added IP: {user_ip} at {current_time}")

    try:
        decrypted_key = await decrypt_part(encrypted_part)

        if not decrypted_key.startswith(OUTLINE_SALT):
            raise HTTPException(status_code=400, detail="Invalid requests")

        hex_id = decrypted_key[len(OUTLINE_SALT):]
        user_id = int(hex_id, 16)
    except Exception as e:
        logging.error(f"Error decrypting key: {str(e)}")
        raise HTTPException(status_code=404, detail="User not found")

    sub = await methods.get_subscription(db, user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="User not found")

    servers = await methods.get_servers(db)
    return {"subscription": sub, "servers": servers}

@app.get('/check-access')
async def check_access(request: Request):
    user_ip = request.client.host

    if user_ip not in active_ips:
        raise HTTPException(status_code=403, detail="Access denied. IP not found.")

    return {"status": "Access granted"}
