from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from telegram_bot.database.context_manager import DatabaseContextManager
from telegram_bot.lexicon.lexicon_ru import LEXICON_RU
from telegram_bot.logger.logging_config import logger
from telegram_bot.models.models import Users
from telegram_bot.services.send_sms_admins import notify_group

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['start'])
    user = Users(
        tg_id=message.from_user.id,
        username=message.from_user.username,
    )
    async with DatabaseContextManager() as session_methods:
        try:
            status_user = await session_methods.users.add_user(user)
            if status_user:
                await notify_group(
                    message=f'Пользователь: @{message.from_user.username}\n'
                            f'ID: {message.from_user.id}\n'
                            f'Присоединился к нам в команду\n#start')
            await session_methods.session.commit()
        except Exception as e:
            logger.error('При кнопке старт произошла ошибка', e)

