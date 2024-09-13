from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.kb_reply import ReplyKeyboards

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Это инлайн-кнопки с параметром "url"',
        reply_markup=ReplyKeyboards.start_keyboard()
    )
