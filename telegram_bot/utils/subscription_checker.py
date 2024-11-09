import asyncio
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import SubscriptionCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from models.models import SubscriptionStatusEnum


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
            try:
                await process_subscription(bot, sub, current_date, session_methods)
            except Exception as e:
                await session_methods.session.rollback()
                await logger.log_error('При проверке подписки произошла ошибка', e)


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
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text='⏳ Продлить подписку',
            callback_data=SubscriptionCallbackFactory(
                action='extend_subscription',
                subscription_id=sub.subscription_id
            ).pack())
    )

    await bot.send_message(
        chat_id=sub.user_id,
        text=LEXICON_RU['reminder_sent'],
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )

    await session_methods.subscription.update_sub(
        subscription_id=sub.subscription_id,
        reminder_sent=1
    )
    await session_methods.session.commit()
    await logger.log_info(
        f"Подписка у пользователя с ID {sub.user_id} истечет через 3 дня.\nКлюч <pre>{sub.key}</pre> будет заблокирован."
    )


async def handle_expired_subscription(bot: Bot, sub, session_methods):
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
    await logger.log_info(
        f"Подписка у пользователя с ID {sub.user_id} истекла.\nКлюч <pre>{sub.key}</pre> заблокирован."
    )


async def handle_subscription_deletion(sub, session_methods):
    result = await session_methods.subscription.delete_sub(subscription_id=sub.subscription_id)
    if not result:
        await logger.log_error('Не удалось удалить подписку при ее истечении', Exception)
        return

    await session_methods.session.commit()
    await logger.log_info(
        f"Подписка у пользователя с ID {sub.user_id} полностью удалена.\nКлюч <pre>{sub.key}</pre> удалён."
    )


async def run_checker(bot: Bot):
    while True:
        await check_subscriptions(bot)
        await asyncio.sleep(3600)
