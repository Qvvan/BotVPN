import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config_data import config
from database.init_db import DataBase
from handlers.admin import add_server, del_key, key_info, add_key, refund, help_info, cancel, block_key, unblock_key, \
    ban_user, unban_user
from handlers.user import createorder, subs, start, support
from keyboards.set_menu import set_main_menu
from logger.logging_config import logger
from middleware.logging_middleware import CallbackLoggingMiddleware, MessageLoggingMiddleware
from services.subscription_checker import run_checker


async def on_startup(bot: Bot):
    """Оповещение администраторов о запуске бота."""
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "Бот запущен.")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения администратору {admin_id}: {e}")


async def on_shutdown(bot: Bot):
    """Оповещение администраторов о завершении работы бота."""
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "Бот завершает работу.")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения администратору {admin_id}: {e}")


async def main():
    logger.info('Starting bot')

    db = DataBase()
    await db.create_db()

    storage = MemoryStorage()

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=storage)

    await set_main_menu(bot)

    dp.message.outer_middleware(MessageLoggingMiddleware())
    dp.callback_query.outer_middleware(CallbackLoggingMiddleware())

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # user-handlers
    dp.include_router(createorder.router)
    dp.include_router(subs.router)
    dp.include_router(start.router)
    dp.include_router(support.router)

    # admin-handlers
    dp.include_router(add_key.router)
    dp.include_router(add_server.router)
    dp.include_router(ban_user.router)
    dp.include_router(block_key.router)
    dp.include_router(del_key.router)
    dp.include_router(help_info.router)
    dp.include_router(key_info.router)
    dp.include_router(refund.router)
    dp.include_router(unban_user.router)
    dp.include_router(unblock_key.router)

    dp.include_router(cancel.router)

    asyncio.create_task(run_checker(bot))

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def run_bot():
    while True:
        try:
            await main()
        except Exception as e:
            logger.error(f"Бот завершил работу с ошибкой: {e}")
            logger.info("Перезапуск бота через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_bot())
