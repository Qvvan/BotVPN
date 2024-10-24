from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from keyboards.kb_inline import InlineKeyboards
from logger.logging_config import logger
from state.state import BanUser

router = Router()


@router.message(Command(commands='ban_user'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(
        text='Отправь ID пользователя и я его заблокирую',
        reply_markup=await InlineKeyboards.cancel(),
    )
    await state.set_state(BanUser.waiting_user_id)


@router.message(BanUser.waiting_user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    user_id = int(message.text)

    async with DatabaseContextManager() as session_methods:
        result = await ban_user(user_id, session_methods)

        if result['success']:
            await message.answer('Пользователь успешно заблокирован')
            await session_methods.session.commit()
        else:
            await message.answer(result['message'])
            await session_methods.session.rollback()

    await state.clear()


async def ban_user(user_id: int, session) -> dict:
    """
    Блокирует пользователя в базе данных.
    :param user_id: ID пользователя
    :param session: сессия базы данных
    :return: dict с результатом операции
    """
    try:
        # Получаем информацию о пользователе
        user_info = await session.users.get_user(user_id)
        if not user_info:
            return {'success': False, 'message': 'Пользователь не найден в базе'}

        if user_info.ban == 1:
            return {'success': False, 'message': 'Пользователь уже заблокирован'}

        await session.users.ban_user(user_id=user_id)

        return {'success': True, 'message': 'Пользователь успешно заблокирован'}

    except Exception as e:
        await logger.log_error('Произошла ошибка при блокировке пользователя', e)
        return {'success': False, 'message': f'Произошла ошибка при блокировке пользователя: {str(e)}'}
