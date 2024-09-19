from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from environs import Env

from config_data.config import ADMIN_IDS
from filters.admin import IsAdmin

env = Env()
router = Router()

admin_ids = [int(admin_id) for admin_id in ADMIN_IDS]


@router.message(IsAdmin(admin_ids), Command(commands='add_admin'))
async def answer_if_admins_update(message: Message):
    await message.answer(text='Вы админ')
