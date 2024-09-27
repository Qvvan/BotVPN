import asyncio
from datetime import datetime, timedelta

from aiogram import Bot

from database.context_manager import DatabaseContextManager
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from models.models import Subscriptions, SubscriptionStatusEnum
from outline.outline_manager.outline_manager import OutlineManager


async def check_subscriptions(bot: Bot):
    async with DatabaseContextManager() as session_methods:
        try:
            manager = OutlineManager()
            await manager.wait_for_initialization()

            subs = await session_methods.subscription.get_subs()

            if subs:
                current_date = datetime.utcnow() + timedelta(hours=3)

                for sub in subs:
                    if sub.status != SubscriptionStatusEnum.ACTIVE:
                        continue
                    if sub.end_date < current_date:
                        await session_methods.subscription.update_sub(Subscriptions(
                            user_id=sub.user_id,
                            service_id=sub.service_id,
                            vpn_key_id=sub.vpn_key_id,
                            start_date=sub.start_date,
                            end_date=sub.end_date,
                            status=SubscriptionStatusEnum.EXPIRED,
                        ))

                        server_info = await session_methods.servers.get_server_by_vpn_key_id(sub.vpn_key_id)

                        await session_methods.vpn_keys.update_limit(vpn_key_id=sub.vpn_key_id, new_limit=1)

                        server_id = server_info[0]
                        outline_vpn_key_id = server_info[1]

                        await manager.upd_limit(server_id, outline_vpn_key_id)

                        await bot.send_message(
                            chat_id=sub.user_id,
                            text=LEXICON_RU['expired'],
                        )
                        logger.info(
                            f"Подписка {sub.subscription_id} истекла. Ключ {sub.vpn_key_id} заблокирован.")

                await session_methods.session.commit()
        except Exception as e:
            logger.error(f'Ошибка при получении подписок', e)
            await session_methods.session.rollback()
            return


async def run_checker(bot: Bot):
    while True:
        logger.info("Running subscription checker...")
        await check_subscriptions(bot)
        await asyncio.sleep(600)
