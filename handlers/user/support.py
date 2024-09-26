from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU

router = Router()


@router.message(Command(commands='support'))
async def get_support(message: Message):
    await message.answer(
        text=LEXICON_RU['support'],
        reply_markup=await InlineKeyboards.get_support(),
    )
