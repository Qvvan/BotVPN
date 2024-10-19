from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update

from logger.logging_config import logger


class MessageLoggingMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.chat.id
        username = event.chat.username
        text = event.text
        logger.info(f"Пользователь {username} (ID: {user_id}) отправил сообщение: {text}")

        return await handler(event, data)


class CallbackLoggingMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        username = event.from_user.username
        button_text = event.data
        logger.info(f"Пользователь {username} (ID: {user_id}) нажал кнопку: {button_text}")

        return await handler(event, data)
