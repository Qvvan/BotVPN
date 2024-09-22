from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from outline_vpn.outline_vpn import OutlineVPN

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from outline.outline_manager.outline_manager import OutlineManager
from state.state import DeleteKey

router = Router()


@router.message(Command(commands='del_key'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(text='Отправь VPN ключ и я его тут же удалю')
    await state.set_state(DeleteKey.waiting_key_code)


@router.message(DeleteKey.waiting_key_code)
async def process_api_url(message: types.Message, state: FSMContext):
    vpn_code = message.text
    # manager = OutlineManager()
    async with DatabaseContextManager() as session_methods:
        try:
            await session_methods.vpn_keys.del_key(vpn_code)
            await message.answer('Ключ успешно удален')
        except Exception as e:
            await message.answer(text=f'Не удалось удалить ключ:\n{e}')

    await state.clear()