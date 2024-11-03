from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from keyboards.kb_inline import InlineKeyboards
from logger.logging_config import logger
from state.state import UnblockKey

router = Router()


@router.message(Command(commands='unblock_key'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(
        text='Отправь VPN ключ и я его разблокирую',
        reply_markup=await InlineKeyboards.cancel(),
    )
    await state.set_state(UnblockKey.waiting_key_unblock)


@router.message(UnblockKey.waiting_key_unblock)
async def process_api_url(message: types.Message, state: FSMContext):
    vpn_code = message.text
    async with DatabaseContextManager() as session_methods:
        result = await unblock_key(vpn_code, session_methods)

        if result['success']:
            await message.answer('Ключ успешно разблокирован')
            await session_methods.session.commit()
        else:
            await message.answer(result['message'])
            await session_methods.session.rollback()

    await state.clear()


async def unblock_key(vpn_code: str, session) -> dict:
    """
    Разблокирует VPN ключ в базе данных и менеджере Outline.
    :param vpn_code: код VPN ключа
    :param session: сессия базы данных
    :return: dict с результатом операции
    """

    try:
        vpn_key_info = await session.vpn_keys.get_key_id(vpn_code)
        if not vpn_key_info:
            return {'success': False, 'message': 'Такого ключа нет в базе'}

        if vpn_key_info.is_limit == 0:
            return {'success': False, 'message': 'Ключ уже разблокирован'}

        await session.vpn_keys.update_limit(vpn_key_id=vpn_key_info.vpn_key_id, new_limit=0)

        return {'success': True, 'message': 'Ключ успешно разблокирован'}

    except Exception as e:
        await logger.log_error('Произошла ошибка при разблокировке ключа', e)
        return {'success': False, 'message': f'Произошла ошибка при разблокировке ключа: {str(e)}'}
