from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from keyboards.kb_inline import InlineKeyboards
from logger.logging_config import logger
from state.state import UnbanUser  # Предположим, что у вас есть состояние UnbanUser

router = Router()


@router.message(Command(commands='unban_user'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(
        text='Отправь ID пользователя и я его разблокирую',
        reply_markup=await InlineKeyboards.cancel(),
    )
    await state.set_state(UnbanUser.waiting_user_id)


@router.message(UnbanUser.waiting_user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    user_id = int(message.text)

    async with DatabaseContextManager() as session_methods:
        result = await unban_user(user_id, session_methods)

        if result['success']:
            await message.answer('Пользователь успешно разблокирован')
            await session_methods.session.commit()
        else:
            await message.answer(result['message'])
            await session_methods.session.rollback()

    await state.clear()


async def unban_user(user_id: int, session) -> dict:
    """
    Разблокирует пользователя в базе данных.
    :param user_id: ID пользователя
    :param session: сессия базы данных
    :return: dict с результатом операции
    """
    try:
        user_info = await session.users.get_user(user_id)
        if not user_info:
            return {'success': False, 'message': 'Пользователь не найден в базе'}

        if user_info.ban == 0:
            return {'success': False, 'message': 'Пользователь уже разблокирован'}

        # Обновляем статус пользователя
        await session.users.unban_user(user_id=user_id)

        return {'success': True, 'message': 'Пользователь успешно разблокирован'}

    except Exception as e:
        await logger.log_error('Произошла ошибка при разблокировке пользователя', e)
        return {'success': False, 'message': f'Произошла ошибка при разблокировке пользователя: {str(e)}'}
