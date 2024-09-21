import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import ADMIN_IDS
from config_data.config import load_config, Config
from database.init_db import DataBase
from handlers import user_handlers, kb_handlers, invoice_handlers, admin_handlers
from handlers.admin import add_server, del_key
from keyboards.set_menu import set_main_menu
from logger.logging_config import logger


async def on_startup(bot: Bot):
    """Оповещение администраторов о запуске бота."""
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "Бот запущен.")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения администратору {admin_id}: {e}")


async def on_shutdown(bot: Bot):
    """Оповещение администраторов о завершении работы бота."""
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "Бот завершает работу.")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения администратору {admin_id}: {e}")


async def main():
    logger.info('Starting bot')

    config: Config = load_config()
    db = DataBase()
    await db.create_db()

    storage = MemoryStorage()

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=storage)

    await set_main_menu(bot)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(user_handlers.router)
    dp.include_router(kb_handlers.router)
    dp.include_router(invoice_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(add_server.router)
    dp.include_router(del_key.router)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
