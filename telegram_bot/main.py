import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config_data import config
from database.init_db import DataBase
from handlers.admin import add_server, key_info, unban_user, block_key, cancel, refund, del_key, \
    unblock_key, help_info, ban_user, pushes, show_servers, active
from handlers.services import payments_service, guide_install
from handlers.user import subs, replace_server, replace_app
from handlers.user import start, support, createorder
from keyboards.set_menu import set_main_menu
from logger.logging_config import logger
from middleware.logging_middleware import CallbackLoggingMiddleware, MessageLoggingMiddleware
from middleware.trottling import ThrottlingMiddleware
from utils import check_servers
from utils.check_servers import ping_servers
from utils.subscription_checker import run_checker


async def on_startup(bot: Bot):
    """Оповещение администраторов о запуске бота."""
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "Бот запущен.")
        except Exception as e:
            await logger.log_error(f"Ошибка отправки сообщения администратору {admin_id}", e)


async def on_shutdown(bot: Bot):
    """Оповещение администраторов о завершении работы бота."""
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "Бот завершает работу.")
        except Exception as e:
            await logger.log_error(f"Ошибка отправки сообщения администратору {admin_id}", e)


async def main():
    await logger.info('Starting bot')

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

    throttling_middleware = ThrottlingMiddleware(limit=0.6)
    dp.message.outer_middleware(throttling_middleware)
    dp.callback_query.outer_middleware(throttling_middleware)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # user-handlers
    dp.include_router(createorder.router)
    dp.include_router(subs.router)
    dp.include_router(start.router)
    dp.include_router(support.router)
    dp.include_router(payments_service.router)
    dp.include_router(replace_server.router)
    dp.include_router(replace_app.router)
    dp.include_router(guide_install.router)

    # admin-handlers
    dp.include_router(add_server.router)
    dp.include_router(ban_user.router)
    dp.include_router(block_key.router)
    dp.include_router(del_key.router)
    dp.include_router(help_info.router)
    dp.include_router(key_info.router)
    dp.include_router(refund.router)
    dp.include_router(unban_user.router)
    dp.include_router(unblock_key.router)
    dp.include_router(pushes.router)
    dp.include_router(check_servers.router)
    dp.include_router(show_servers.router)
    dp.include_router(active.router)

    dp.include_router(cancel.router)

    asyncio.create_task(run_checker(bot))
    asyncio.create_task(ping_servers(bot))

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
            await logger.log_error(f"Бот завершил работу с ошибкой", e)
            await logger.info("Перезапуск бота через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_bot())
