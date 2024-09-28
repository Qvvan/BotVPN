from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from keyboards.kb_inline import InlineKeyboards
from outline.outline_manager.outline_manager import OutlineManager
from state.state import DeleteKey

router = Router()


@router.message(Command(commands='del_key'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(
        text='Отправь VPN ключ и я его тут же удалю',
        reply_markup=await InlineKeyboards.cancel()
    )
    await state.set_state(DeleteKey.waiting_key_code)


@router.message(DeleteKey.waiting_key_code)
async def process_api_url(message: types.Message, state: FSMContext):
    vpn_code = message.text
    manager = OutlineManager()
    await manager.wait_for_initialization()
    async with DatabaseContextManager() as session_methods:
        try:
            vpn_key_info = await session_methods.vpn_keys.get_key_id(vpn_code)
            if not vpn_key_info:
                await message.answer('Такого ключа не существует')
            else:
                await session_methods.vpn_keys.del_key(vpn_code)
                await manager.delete_key(vpn_key_info.server_id, vpn_key_info.outline_key_id)
                await message.answer('Ключ успешно удален')
                await session_methods.session.commit()
        except Exception as e:
            await session_methods.session.rollback()
            await message.answer(text=f'Не удалось удалить ключ:\n{e}')

    await state.clear()