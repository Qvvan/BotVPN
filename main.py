import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_data.config import load_config, Config
from database.db import DB
from database.init_db.init_db import init_db
from handlers import user_handlers, kb_handlers, invoice_handlers
from models.models import Users

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config: Config = load_config()

    init_db(config)

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(user_handlers.router)
    dp.include_router(kb_handlers.router)
    dp.include_router(invoice_handlers.router)

    # async def test_add_user_and_service():
    #     try:
    #         # Начало транзакции
    #         DB.get().connection.begin()
    #         logger.info("Transaction started for adding user and service.")
    #
    #         # Добавляем пользователя
    #         user = Users(tg_id="123456789", username="Test User")
    #         DB.get().users.add_user(user)
    #         logger.info(f"User added: {user}")
    #
    #         # Добавляем сервис
    #         service = DB.get().services.add_service(name="Test Service", duration_days=30, price=100)
    #         logger.info(f"Service added: {service}")
    #
    #         # Коммит транзакции
    #         DB.get().connection.commit()
    #         logger.info("Transaction committed successfully.")
    #     except Exception as e:
    #         # Обработка ошибок и откат транзакции в случае исключения
    #         logger.error(f"Error during adding user and service: {e}")
    #         DB.get().connection.rollback()
    #         logger.warning("Transaction rolled back due to an error.")
    #
    # await test_add_user_and_service()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)




if __name__ == "__main__":
    asyncio.run(main())
