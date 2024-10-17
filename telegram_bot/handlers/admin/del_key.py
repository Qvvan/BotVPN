from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from telegram_bot.config_data.config import ADMIN_IDS
from telegram_bot.database.context_manager import DatabaseContextManager
from telegram_bot.filters.admin import IsAdmin
from telegram_bot.keyboards.kb_inline import InlineKeyboards
from telegram_bot.outline.outline_manager.outline_manager import OutlineManager
from telegram_bot.state.state import DeleteKey

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
    async with DatabaseContextManager() as session_methods:
        result = await delete_key(vpn_code, session_methods)

        if result['success']:
            await message.answer('Ключ успешно удален')
            await session_methods.session.commit()
        else:
            await message.answer(result['message'])
            await session_methods.session.rollback()

    await state.clear()


async def delete_key(vpn_code, session):
    """
    Удаляет VPN ключ из базы данных и менеджера Outline.
    :param vpn_code: код VPN ключа
    :param session: сессия базы данных
    :return: dict с результатом операции
    """
    manager = OutlineManager()
    await manager.wait_for_initialization()

    try:
        vpn_key_info = await session.vpn_keys.get_key_id(vpn_code)
        if not vpn_key_info:
            return {'success': False, 'message': 'Такого ключа не существует'}

        await session.vpn_keys.del_key(vpn_code)
        await manager.delete_key(vpn_key_info.server_id, vpn_key_info.outline_key_id)

        return {'success': True, 'message': 'Ключ успешно удален'}

    except Exception as e:
        return {'success': False, 'message': f'Не удалось удалить ключ: {str(e)}'}
