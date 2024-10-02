import asyncio
from datetime import datetime, timedelta

from aiogram import Bot

from database.context_manager import DatabaseContextManager
from handlers.admin.block_key import block_key
from handlers.admin.del_key import delete_key
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from models.models import Subscriptions, SubscriptionStatusEnum


async def check_subscriptions(bot: Bot):
    async with DatabaseContextManager() as session_methods:
        try:
            subs = await session_methods.subscription.get_subs()
            if not subs:
                return
        except Exception as e:
            logger.error(f'Ошибка при получении подписок', e)
            return

    current_date = datetime.utcnow() + timedelta(hours=3)
    for sub in subs:
        async with DatabaseContextManager() as session_methods:
            try:
                await process_subscription(bot, sub, current_date, session_methods)
            except Exception as e:
                await session_methods.session.rollback()
                logger.error('При проверке подписки произошла ошибка', e)


async def process_subscription(bot: Bot, sub, current_date, session_methods):
    days_since_expiration = (current_date - sub.end_date).days
    days_until_end = (sub.end_date - current_date).days
    server_info = await session_methods.vpn_keys.get_by_id(sub.vpn_key_id)

    if days_until_end == 3 and not sub.reminder_sent:
        await send_reminder(bot, sub, session_methods)

    elif sub.end_date < current_date and sub.reminder_sent:
        await handle_expired_subscription(bot, sub, server_info, session_methods)

    elif days_since_expiration > 5:
        await handle_subscription_deletion(sub, server_info, session_methods)


async def send_reminder(bot: Bot, sub, session_methods):
    await bot.send_message(
        chat_id=sub.user_id,
        text=LEXICON_RU['reminder_sent'],
        parse_mode="HTML"
    )

    await session_methods.subscription.update_sub(Subscriptions(
        user_id=sub.user_id,
        service_id=sub.service_id,
        vpn_key_id=sub.vpn_key_id,
        start_date=sub.start_date,
        end_date=sub.end_date,
        status=sub.status,
        reminder_sent=1
    ))
    await session_methods.session.commit()
    logger.info(
        f"Подписка {sub.subscription_id} истечет через 3 дня. Ключ {sub.vpn_key_id} будет заблокирован."
    )


async def handle_expired_subscription(bot: Bot, sub, server_info, session_methods):
    await session_methods.subscription.update_sub(Subscriptions(
        user_id=sub.user_id,
        service_id=sub.service_id,
        vpn_key_id=sub.vpn_key_id,
        start_date=sub.start_date,
        end_date=sub.end_date,
        status=SubscriptionStatusEnum.EXPIRED,
    ))

    result = await block_key(server_info.key, session_methods)
    if result['success']:
        await session_methods.session.commit()
        await bot.send_message(
            chat_id=sub.user_id,
            text=LEXICON_RU['expired'],
        )
        logger.info(
            f"Подписка {sub.subscription_id} истекла. Ключ {sub.vpn_key_id} заблокирован."
        )
    else:
        await session_methods.session.rollback()
        logger.error(result['message'])


async def handle_subscription_deletion(sub, server_info, session_methods):
    result = await session_methods.subscription.delete_sub(subscription_id=sub.subscription_id)
    if not result:
        logger.error('Не удалось удалить подписку при ее истечении')
        return

    result = await delete_key(server_info.key, session_methods)
    if result['success']:
        await session_methods.session.commit()
        logger.info(
            f"Подписка {sub.subscription_id} полностью удалена. Ключ {sub.vpn_key_id} удалён."
        )
    else:
        await session_methods.session.rollback()
        logger.error(result['message'])


async def run_checker(bot: Bot):
    while True:
        logger.info("Running subscription checker...")
        await check_subscriptions(bot)
        await asyncio.sleep(3600)
