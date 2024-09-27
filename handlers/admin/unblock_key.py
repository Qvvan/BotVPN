from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from logger.logging_config import logger
from outline.outline_manager.outline_manager import OutlineManager
from state.state import UnblockKey

router = Router()


@router.message(Command(commands='unblock_key'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(text='Отправь VPN ключ и я его разблокирую')
    await state.set_state(UnblockKey.waiting_key_unblock)


@router.message(UnblockKey.waiting_key_unblock)
async def process_api_url(message: types.Message, state: FSMContext):
    vpn_code = message.text
    manager = OutlineManager()
    await manager.wait_for_initialization()
    async with DatabaseContextManager() as session_methods:
        try:
            vpn_key_info = await session_methods.vpn_keys.get_key_id(vpn_code)
            if not vpn_key_info:
                await message.answer('Такого ключа нет в базе')
            elif vpn_key_info.is_limit == 0:
                await message.answer('Ключ уже разблокирован')
            elif vpn_key_info:
                await session_methods.vpn_keys.update_limit(vpn_key_id=vpn_key_info.vpn_key_id, new_limit=0)

                await manager.delete_key(vpn_key_info.server_id, vpn_key_info.outline_key_id)
                await session_methods.session.commit()
                await message.answer('Ключ успешно разблокирован')
        except Exception as e:
            await session_methods.session.rollback()
            await message.answer(f'Произошла ошибка при разблокировке ключа:\n{e}')
            logger.error('Произошла ошибка при разблокировке ключа', e)

        await state.clear()
