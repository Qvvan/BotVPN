from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from database.db import DB
from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from models.models import Users

router = Router()

@router.message(CommandStart())
async def process_start_command(message: Message):
    user = Users(
        tg_id=str(message.from_user.id),
        username=message.from_user.username,
    )
    DB.get().users.add_user(user)
    await message.answer(text=LEXICON_RU['start'])

@router.message(Command(commands='createorder'))
async def create_order(message: Message):
    await message.answer(text=LEXICON_RU['createorder'], reply_markup=InlineKeyboards.create_order_keyboards())