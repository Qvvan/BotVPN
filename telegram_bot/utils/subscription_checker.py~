import asyncio
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.context_manager import DatabaseContextManager
from handlers.services.get_session_cookies import get_session_cookie
from handlers.services.key_create import BaseKeyManager
from keyboards.kb_inline import SubscriptionCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from models.models import SubscriptionStatusEnum, Users


async def check_subscriptions(bot: Bot):
    async with DatabaseContextManager() as session_methods:
        try:
            subs = await session_methods.subscription.get_subs()
            if not subs:
                return
        except Exception as e:
            await logger.log_error(f'Ошибка при получении подписок', e)
            return

    current_date = datetime.utcnow() + timedelta(hours=3)
    for sub in subs:
        async with DatabaseContextManager() as session_methods:
            await process_subscription(bot, sub, current_date, session_methods)


async def process_subscription(bot: Bot, sub, current_date, session_methods):
    days_since_expiration = (current_date - sub.end_date).days
    days_until_end = (sub.end_date - current_date).days

    if days_until_end == 3 and not sub.reminder_sent:
        await send_reminder(bot, sub, session_methods)

    elif sub.end_date < current_date and sub.reminder_sent:
        await handle_expired_subscription(bot, sub, session_methods)

    elif days_since_expiration > 5:
        await handle_subscription_deletion(sub, session_methods)


async def send_reminder(bot: Bot, sub, session_methods):
    user = Users(username='None')
    try:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(
                text='⏳ Продлить подписку',
                callback_data=SubscriptionCallbackFactory(
                    action='extend_subscription',
                    subscription_id=sub.subscription_id
                ).pack())
        )
        await session_methods.subscription.update_sub(
            subscription_id=sub.subscription_id,
            reminder_sent=1
        )
        await session_methods.session.commit()
        await bot.send_message(
            chat_id=sub.user_id,
            text=LEXICON_RU['reminder_sent'],
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )
        user = await session_methods.users.get_user(sub.user_id)
        await logger.log_info(
            f"Подписка у пользователя:\nID: {sub.user_id}\nUsername: @{user.username}\nИстечет через 3 дня."
        )
    except Exception as e:
        await session_methods.session.rollback()
        await logger.log_error(
            f'Пользователь:\nID: {sub.user_id}\nUsername: @{user.username}\nОшибка при отправке напоминания', e)


async def handle_expired_subscription(bot: Bot, sub, session_methods):
    user = Users(username='None')
    try:
        await session_methods.subscription.update_sub(
            subscription_id=sub.subscription_id,
            status=SubscriptionStatusEnum.EXPIRED,
            reminder_sent=0,
        )

        await session_methods.session.commit()
        await bot.send_message(
            chat_id=sub.user_id,
            text=LEXICON_RU['expired'],
        )
        user = await session_methods.users.get_user(sub.user_id)
        await logger.log_info(
            f"Подписка у пользователя:\nID: {sub.user_id}\nUsername: @{user.username}\nИстекла"
        )
        session = await get_session_cookie(sub.server_ip)
        await BaseKeyManager(server_ip=sub.server_ip, session_cookie=session).update_key_enable(sub.key_id, False)
    except Exception as e:
        await session_methods.session.rollback()
        await logger.log_error(
            f'Пользователь:\nID: {sub.user_id}\nUsername: @{user.username}\nОшибка при обновлении подписки', e)


async def handle_subscription_deletion(sub, session_methods):
    user = Users(username='None')
    try:
        result = await session_methods.subscription.delete_sub(subscription_id=sub.subscription_id)
        if not result:
            await logger.log_error('Не удалось удалить подписку при ее истечении', Exception)
            return

        await session_methods.session.commit()
        user = await session_methods.users.get_user(sub.user_id)
        await logger.log_info(
            f"Подписка у пользователя:\nID: {sub.user_id}\nUsername: @{user.username}\nПолностью удалена"
        )
        session = await get_session_cookie(sub.server_ip)
        await BaseKeyManager(server_ip=sub.server_ip, session_cookie=session).delete_key(sub.key_id)
    except Exception as e:
        await session_methods.session.rollback()
        await logger.log_error(
            f'Пользователь:\nID: {sub.user_id}\nUsername: @{user.username}\nОшибка при удалении подписки', e)


async def run_checker(bot: Bot):
    while True:
        await check_subscriptions(bot)
        await asyncio.sleep(3600)
