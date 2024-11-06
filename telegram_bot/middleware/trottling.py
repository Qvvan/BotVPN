from __future__ import annotations

import time
from typing import *

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import logger


def rate_limit(limit: int, key=None):
    """
    Decorator for configuring rate limit and key in different functions.

    :param limit:
    :param key:
    :return:
    """

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit=0.5, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        self.throttle_manager = ThrottleManager()
        super(ThrottlingMiddleware, self).__init__()

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        global result
        try:
            await self.on_process_event(event, data)
        except CancelHandler:
            # Cancel current handler
            return

        try:
            result = await handler(event, data)
        except Exception as e:
            logger.exception(e)

        return result

    async def on_process_event(
            self,
            event: Union[Message, CallbackQuery],
            data: dict,
    ) -> Any:
        limit = getattr(data["handler"].callback, "throttling_rate_limit", self.rate_limit)
        key = getattr(data["handler"].callback, "throttling_key", f"{self.prefix}_message")

        user_id = event.from_user.id
        chat_id = getattr(event, "chat", None).id if isinstance(event, Message) else user_id

        try:
            await self.throttle_manager.throttle(key, rate=limit, user_id=user_id, chat_id=chat_id)
        except Throttled as t:
            await self.event_throttled(event, t)
            raise CancelHandler()

    async def event_throttled(self, event: Message, throttled: Throttled):
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count <= 2:
            await event.answer(
                f'⚠️ Пожалуйста, не нажимай на кнопки так часто! 😅 Дай мне немного времени, чтобы обработать твой запрос')

    async def is_throttled(self, event: Union[Message, CallbackQuery]) -> bool:
        limit = self.rate_limit
        key = f"{self.prefix}_message"
        user_id = event.from_user.id
        chat_id = getattr(event, "chat", None).id if isinstance(event, Message) else user_id

        try:
            await self.throttle_manager.throttle(key, rate=limit, user_id=user_id, chat_id=chat_id)
            return False  # Не заблокирован
        except Throttled:
            return True  # Заблокирован


class ThrottleManager:
    bucket_keys = [
        "RATE_LIMIT", "DELTA",
        "LAST_CALL", "EXCEEDED_COUNT"
    ]

    def __init__(self):
        self.data = {}

    async def throttle(self, key: str, rate: float, user_id: int, chat_id: int):
        now = time.time()
        bucket_name = f'throttle_{key}_{user_id}_{chat_id}'

        data = self.data.get(bucket_name, {
            "RATE_LIMIT": rate,
            "LAST_CALL": now,
            "DELTA": 0,
            "EXCEEDED_COUNT": 0,
        })

        # Calculate
        called = data.get("LAST_CALL", now)
        delta = now - called
        result = delta >= rate or delta <= 0

        # Update data
        data["RATE_LIMIT"] = rate
        data["LAST_CALL"] = now
        data["DELTA"] = delta
        if not result:
            data["EXCEEDED_COUNT"] += 1
        else:
            data["EXCEEDED_COUNT"] = 1

        self.data[bucket_name] = data

        if not result:
            raise Throttled(key=key, chat=chat_id, user=user_id, **data)

        return result


class Throttled(Exception):
    def __init__(self, **kwargs):
        self.key = kwargs.pop("key", '<None>')
        self.called_at = kwargs.pop("LAST_CALL", time.time())
        self.rate = kwargs.pop("RATE_LIMIT", None)
        self.exceeded_count = kwargs.pop("EXCEEDED_COUNT", 0)
        self.delta = kwargs.pop("DELTA", 0)
        self.user = kwargs.pop('user', None)
        self.chat = kwargs.pop('chat', None)

    def __str__(self):
        return f"Rate limit exceeded! (Limit: {self.rate} s, " \
               f"exceeded: {self.exceeded_count}, " \
               f"time delta: {round(self.delta, 3)} s)"


class CancelHandler(Exception):
    pass
