import asyncio
import ssl

import aiohttp

from config_data.config import MY_SECRET_URL, LOGIN_X_UI_PANEL, PASSWORD_X_UI_PANEL
from logger.logging_config import logger


async def get_session_cookie(server_ip: str) -> str:
    url = f"https://{server_ip}:54321/{MY_SECRET_URL}/login"
    payload = {
        "username": LOGIN_X_UI_PANEL,
        "password": PASSWORD_X_UI_PANEL
    }

    # Создаем контекст SSL для отключения проверки сертификата
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, ssl=ssl_context, timeout=30) as response:

                if response.status == 200:
                    # Логируем заголовки Set-Cookie
                    set_cookie_headers = response.headers.getall("Set-Cookie")

                    session_value = None
                    for header in set_cookie_headers:
                        if "3x-ui" in header:
                            session_value = header.split("3x-ui=", 1)[1].split(";")[0]

                    if session_value:
                        return session_value
                    else:
                        await logger.log_error(
                            f"Сессионный ключ 3x-ui не найден в Set-Cookie заголовках от {server_ip}", None)

                else:
                    await logger.log_error(f"Неудачный ответ от {server_ip}: статус {response.status}", None)

    except aiohttp.ClientConnectionError as e:
        await logger.log_error(f"Ошибка соединения с {server_ip}", e)
    except aiohttp.ClientPayloadError as e:
        await logger.log_error(f"Ошибка с данными запроса к {server_ip}", e)
    except asyncio.TimeoutError as e:
        await logger.log_error(f"Таймаут при подключении к {server_ip}", e)
    except Exception as e:
        await logger.log_error(f"Неизвестная ошибка при подключении к {server_ip}", e)
