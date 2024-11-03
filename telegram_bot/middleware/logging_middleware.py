from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, Update, ReplyKeyboardRemove
from logger.logging_config import logger

class MessageLoggingMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.chat.id
            username = event.chat.username
            text = "Загрузка 🔄"
            await logger.info(f"Пользователь {username} (ID: {user_id}) отправил сообщение: {text}")
            if text:
                sent_message = await event.answer(text, reply_markup=ReplyKeyboardRemove())
                await sent_message.delete()

        return await handler(event, data)


class CallbackLoggingMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        if hasattr(event, 'from_user'):
            user_id = event.from_user.id
            username = event.from_user.username
            button_text = event.data
            await logger.info(f"Пользователь {username} (ID: {user_id}) нажал кнопку: {button_text}")

        return await handler(event, data)