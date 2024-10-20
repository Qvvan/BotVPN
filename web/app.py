import asyncio
import base64
import logging
import re
import json

from cryptography.fernet import Fernet
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from cfg.config import OUTLINE_SALT, CRYPTO_KEY
from db import methods
from db.database import get_db
from outline.outline_manager import OutlineManager

cipher = Fernet(CRYPTO_KEY)
app = FastAPI()

active_ips = {}


async def parse_static_access_key(static_key):
    # Проверяем формат ключа
    match = re.match(r'ss://(.*)@(.*):(\d+)/\?outline=\d+', static_key)
    if not match:
        raise ValueError("Invalid static access key format")

    # Извлекаем части ключа
    encoded_info = match.group(1)
    server = match.group(2)
    server_port = match.group(3)

    # Декодируем информацию
    decoded_info = base64.b64decode(encoded_info).decode('utf-8')
    method, password = decoded_info.split(':')

    access_info = {
        "server": server,
        "server_port": server_port,
        "password": password,
        "method": method
    }

    return access_info


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
    current_time = asyncio.get_event_loop().time()
    print(f"Added IP: {user_ip} at {current_time}")

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
    for server in servers:
        outline_manager = OutlineManager(api_url=server.api_url, cert_sha256=server.cert_sha256)
        await outline_manager.delete_key(user_id)
        if len(await outline_manager.get_keys()) <= 12:
            key = await outline_manager.create_key(str(user_id))
            return type(await parse_static_access_key(static_key=key.access_url))


@app.get('/check-access')
async def check_access(request: Request):
    user_ip = request.client.host

    if user_ip not in active_ips:
        raise HTTPException(status_code=403, detail="Access denied. IP not found.")

    return {"status": "Access granted"}
