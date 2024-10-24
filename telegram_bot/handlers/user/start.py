from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from models.models import Users

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text=LEXICON_RU['start'],
        reply_markup=await InlineKeyboards.show_start_menu()
    )
    user = Users(
        tg_id=message.from_user.id,
        username=message.from_user.username,
    )
    async with DatabaseContextManager() as session_methods:
        try:
            status_user = await session_methods.users.add_user(user)
            if status_user:
                logger.log_info(
                    f"К нам присоединился:\n"
                    f"Имя: @{message.from_user.username}\n"
                    f"id: {message.from_user.id}")
            await session_methods.session.commit()
        except Exception as e:
            logger.log_error(f'Пользователь: @{message.from_user.username}\n'
                             f'При команде /start произошла ошибка:', e)

