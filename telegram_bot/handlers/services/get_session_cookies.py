import aiohttp

from config_data.config import MY_SECRET_URL, LOGIN_X_UI_PANEL, PASSWORD_X_UI_PANEL
from logger.logging_config import logger


async def get_session_cookie(server_ip: str) -> str:
    url = f"https://{server_ip}:54321/{MY_SECRET_URL}/login"
    payload = {
        "username": LOGIN_X_UI_PANEL,
        "password": PASSWORD_X_UI_PANEL
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, ssl=False, timeout=2) as response:
                if response.status == 200:
                    set_cookie_headers = response.headers.getall("Set-Cookie")
                    session_value = None
                    for header in set_cookie_headers:
                        if "3x-ui" in header:
                            session_value = header.split("3x-ui=", 1)[1].split(";")[0]

                    if session_value:
                        return session_value
    except Exception as e:
        await logger.log_error(f"Ошибка при получении сессионного ключа {server_ip}", e)

