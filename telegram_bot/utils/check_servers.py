import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Router
from aiogram.client.session import aiohttp
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config_data.config import PORT_X_UI, MY_SECRET_URL
from database.context_manager import DatabaseContextManager
from handlers.services.get_session_cookies import get_session_cookie
from keyboards.kb_inline import ServerCallbackData
from logger.logging_config import logger

notification_dict = {}

router = Router()


async def ping_servers(bot: Bot):
    while True:
        async with DatabaseContextManager() as session_methods:
            servers = []
            user_subs = []
            try:
                servers = await session_methods.servers.get_all_servers()
                user_subs = await session_methods.subscription.get_subs()
            except Exception as e:
                await logger.log_error("Не удалось взять список серверов, при проверке работоспособности серверов", e)

        for server in servers:
            if server.hidden == 1:
                continue

            reachable = await get_session_cookie(server.server_ip)
            if reachable:
                if server.server_ip in notification_dict:
                    del notification_dict[server.server_ip]
            else:
                button = [InlineKeyboardButton(
                    text="Выключить сервер",
                    callback_data=ServerCallbackData(
                        action='disable',
                        server_ip=server.server_ip).pack()
                )]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[button])
                await logger.log_error(
                    message=f'Сервер: {server.server_ip}\n'
                            f'Название: {server.name}',
                    error='⚠️Недоступен ‼',
                    keyboard=keyboard
                )
                if server.server_ip not in notification_dict:
                    notification_dict[server.server_ip] = {}
                #
                # for sub in user_subs:
                #     if server.server_ip in sub.key:
                #         user_id = sub.user_id
                #         last_notified = notification_dict[server.server_ip].get(user_id)
                #         if not last_notified or datetime.now() - last_notified > timedelta(minutes=30):
                #             try:
                #                 await bot.send_message(
                #                     chat_id=user_id,
                #                     text=f"⚠️ Сервер {server.name} временно недоступен! ⚠️\n\n"
                #                          "ℹ️ Мы заметили, что этот сервер выбран в вашей подписке. "
                #                          "Пожалуйста, переключитесь на другой доступный сервер, чтобы продолжить пользоваться услугами. 🙏\n\n"
                #                          "Команда MaskNetVPN уже активно работает над устранением проблемы! 💪🔧\n\n"
                #                          "Благодарим вас за терпение и понимание! 💚"
                #                 )
                #                 notification_dict[server.server_ip][user_id] = datetime.now()
                #             except Exception as e:
                #                 await logger.log_error(f"Ошибка отправки уведомления пользователю {user_id}", e)

        current_time = datetime.now()
        for server_ip in list(notification_dict.keys()):
            for user_id in list(notification_dict[server_ip].keys()):
                if current_time - notification_dict[server_ip][user_id] > timedelta(minutes=30):
                    del notification_dict[server_ip][user_id]
            if not notification_dict[server_ip]:
                del notification_dict[server_ip]

        await asyncio.sleep(60)
