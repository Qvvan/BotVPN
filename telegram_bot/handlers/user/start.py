from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

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
        user_id=message.from_user.id,
        username=message.from_user.username,
    )
    async with DatabaseContextManager() as session_methods:
        try:
            status_user = await session_methods.users.add_user(user)
            if status_user:
                await logger.log_info(
                    f"К нам присоединился:\n"
                    f"Имя: @{message.from_user.username}\n"
                    f"id: {message.from_user.id}")
            await session_methods.session.commit()
        except Exception as e:
            await logger.log_error(f'Пользователь: @{message.from_user.username}\n'
                             f'При команде /start произошла ошибка:', e)


@router.callback_query(lambda c: c.data == 'know_more')
async def handle_know_more(callback: CallbackQuery):
    """Обработчик кнопки 'Узнать больше'."""
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON_RU['know_more'],
        reply_markup=await InlineKeyboards.support_and_subscribe_keyboard()
    )
