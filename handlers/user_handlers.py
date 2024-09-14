from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from database.db import DB
from keyboards.kb_inline import InlineKeyboards
from keyboards.kb_reply import ReplyKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from models.models import Users

router = Router()

@router.message(CommandStart())
async def process_start_command(message: Message):
    user = Users(
        tg_id=message.from_user.id,
        username=message.from_user.username,
    )
    DB.get().add_user(user)
    await message.answer(text=LEXICON_RU['start'], reply_markup=ReplyKeyboards.start_keyboard())

@router.message(Command(commands='createorder'))
async def create_order(message: Message):
    await message.answer(text=LEXICON_RU['createorder'], reply_markup=InlineKeyboards.create_order_keyboards())