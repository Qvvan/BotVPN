from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from state.state import KeyInfo

router = Router()

@router.message(Command(commands='add_server'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(text='Отправьте ключ, для получения полной информации')
    await state.set_state(KeyInfo.waiting_key_info)

@router.message(KeyInfo.waiting_key_info)
async def key_info(message: types.Message, state: FSMContext):
    key = message.text
    async with DatabaseContextManager() as session_methods:
        try:
            session_methods.vpn_keys.key_info()