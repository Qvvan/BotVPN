from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database.context_manager import DatabaseContextManager
from lexicon.lexicon_ru import LEXICON_RU
from models.models import Users

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    user = Users(
        tg_id=message.from_user.id,
        username=message.from_user.username,
    )
    async with DatabaseContextManager() as session_methods:
        await session_methods.users.add_user(user)
        await session_methods.session.commit()
        await message.answer(text=LEXICON_RU['start'])
