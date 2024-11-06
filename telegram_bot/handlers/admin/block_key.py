from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from keyboards.kb_inline import InlineKeyboards
from logger.logging_config import logger
from state.state import KeyBlock

router = Router()


@router.message(Command(commands='block_key'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(
        text='Отправь VPN ключ и я его заблокирую',
        reply_markup=await InlineKeyboards.cancel(),
    )
    await state.set_state(KeyBlock.waiting_key_block)


@router.message(KeyBlock.waiting_key_block)
async def process_api_url(message: types.Message, state: FSMContext):
    vpn_code = message.text
    async with DatabaseContextManager() as session_methods:
        result = await block_key(vpn_code, session_methods)

        if result['success']:
            await message.answer('Ключ успешно заблокирован')
            await session_methods.session.commit()
        else:
            await message.answer(result['message'])
            await session_methods.session.rollback()

    await state.clear()


async def block_key(vpn_code: str, session) -> dict:
    """
    Блокирует VPN ключ в базе данных и менеджере Outline.
    :param vpn_code: код VPN ключа
    :param session: сессия базы данных
    :return: dict с результатом операции
    """


    try:
        # Получаем информацию о VPN ключе
        vpn_key_info = await session.vpn_keys.get_key_id(vpn_code)
        if not vpn_key_info:
            return {'success': False, 'message': 'Такого ключа нет в базе'}

        if vpn_key_info.is_limit == 1:
            return {'success': False, 'message': 'Ключ уже заблокирован'}

        await session.vpn_keys.update_limit(vpn_key_id=vpn_key_info.vpn_key_id, new_limit=1)

        return {'success': True, 'message': 'Ключ успешно заблокирован'}

    except Exception as e:
        await logger.log_error('Произошла ошибка при блокировке ключа', e)
        return {'success': False, 'message': f'Произошла ошибка при блокировке ключа: {str(e)}'}
