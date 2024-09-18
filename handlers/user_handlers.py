from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from database.db_methods import MethodsManager
from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from models.models import Users
from database.init_db import DataBase

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    user = Users(
        tg_id=message.from_user.id,
        username=message.from_user.username,
    )
    db = DataBase()
    async with db.Session() as session:
        session_methods = MethodsManager(session)
        await session_methods.users.add_user(user)
        await session.commit()
        await message.answer(text=LEXICON_RU['start'])


@router.message(Command(commands='createorder'))
async def create_order(message: Message):
    await message.answer(text=LEXICON_RU['createorder'], reply_markup=await InlineKeyboards.create_order_keyboards())
