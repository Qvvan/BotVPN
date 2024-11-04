import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update, ReplyKeyboardRemove

from logger.logging_config import logger

# Задаём параметры антиспама
MINIMUM_TIME_BETWEEN_ACTIONS = 0.4  # Минимальное время между действиями, чтобы не считалось спамом (в секундах)
SPAM_SERIES_THRESHOLD = 2  # Количество быстрых действий подряд, которое считаем спамом
SPAM_WARNING_TIMEOUT = 3  # Время (в секундах), на которое отправляем предупреждение и игнорируем дальнейший спам

# Словари для отслеживания времени и количества быстрых действий, а также отправленных предупреждений
user_last_action_time = {}
user_action_count = {}
user_warning_time = {}


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
            current_time = time.time()

            # Проверка на блокировку пользователя после предупреждения
            if user_id in user_warning_time and current_time - user_warning_time[user_id] < SPAM_WARNING_TIMEOUT:
                # Игнорируем сообщение пользователя в течение SPAM_WARNING_TIMEOUT после предупреждения
                return

            # Проверка на спам: слишком быстрое повторение сообщений/команд
            if user_id in user_last_action_time:
                time_since_last_action = current_time - user_last_action_time[user_id]

                if time_since_last_action < MINIMUM_TIME_BETWEEN_ACTIONS:
                    user_action_count[user_id] += 1
                else:
                    user_action_count[user_id] = 1
            else:
                user_action_count[user_id] = 1

            user_last_action_time[user_id] = current_time

            # Если превышен порог для спама, отправить предупреждение и установить блокировку
            if user_action_count[user_id] >= SPAM_SERIES_THRESHOLD:
                if user_id not in user_warning_time or current_time - user_warning_time[
                    user_id] >= SPAM_WARNING_TIMEOUT:
                    await event.answer(
                        "🚨 Пожалуйста, не отправляйте команды так быстро! 🙏 Дайте мне немного времени, чтобы ответить.",
                        reply_markup=ReplyKeyboardRemove())
                    await logger.log_error(f"Пользователь {username} (ID: {user_id}) спамит командами/кнопками.",
                                           'Спам')
                    user_warning_time[user_id] = current_time
                return

            # Обработка сообщения (например, команда)
            text = "Загрузка 🔄"
            await logger.info(f"Пользователь {username} (ID: {user_id}) отправил сообщение: {event.text}")
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
        if isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            username = event.from_user.username
            button_text = event.data
            current_time = time.time()

            # Проверка на блокировку пользователя после предупреждения
            if user_id in user_warning_time and current_time - user_warning_time[user_id] < SPAM_WARNING_TIMEOUT:
                # Игнорируем нажатие пользователя в течение SPAM_WARNING_TIMEOUT после предупреждения
                return

            # Проверка на спам: слишком быстрое повторение нажатий кнопок
            if user_id in user_last_action_time:
                time_since_last_action = current_time - user_last_action_time[user_id]

                if time_since_last_action < MINIMUM_TIME_BETWEEN_ACTIONS:
                    user_action_count[user_id] += 1
                else:
                    user_action_count[user_id] = 1
            else:
                user_action_count[user_id] = 1

            user_last_action_time[user_id] = current_time

            # Если превышен порог для спама, отправить предупреждение и установить блокировку
            if user_action_count[user_id] >= SPAM_SERIES_THRESHOLD:
                await event.message.answer(
                    "⚠️ Пожалуйста, не нажимайте на кнопки так часто! 😅 Дайте мне немного времени, чтобы обработать ваш запрос.")
                await logger.log_error(f"Пользователь {username} (ID: {user_id}) спамит командами/кнопками.", 'Спам')

                user_warning_time[user_id] = current_time
                return

            # Обработка нажатия кнопки
            await logger.info(f"Пользователь {username} (ID: {user_id}) нажал кнопку: {button_text}")

        return await handler(event, data)
