from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import UserPaginationCallback, InlineKeyboards, UserSelectCallback

router = Router()

@router.message(Command(commands="pushes"))
async def start_broadcast(message: types.Message, state: FSMContext):
    """Начало показа пользователей с кнопками навигации."""
    async with DatabaseContextManager() as session_methods:
        users = await session_methods.users.get_all_users()
        users_dict = {user.user_id: {'user_id': user.user_id, 'username': user.username, 'selected': False} for user in users}
        await state.update_data(users=users_dict)
    page = 1
    await show_users(message, page, users_dict)


@router.callback_query(UserSelectCallback.filter())
async def select_user(callback_query: types.CallbackQuery, callback_data: UserSelectCallback, state: FSMContext):
    data = await state.get_data()
    users_dict = data.get('users', {})
    user_id = callback_data.user_id
    if user_id in users_dict:
        users_dict[user_id]['selected'] = not users_dict[user_id]['selected']
        await state.update_data(users=users_dict)
    page = (list(users_dict.keys()).index(user_id) // 5) + 1
    await show_users(callback_query.message, page, users_dict)
    await callback_query.answer()
    await state.update_data(current_page=page)

@router.callback_query(lambda call: call.data in ['add_all_users', 'add_active_users', 'cancel_all'])
async def handle_special_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    data = await state.get_data()
    users_dict = data.get('users', {})
    if callback_query.data == 'add_all_users':
        for user in users_dict.values():
            user['selected'] = True
    elif callback_query.data == 'add_active_users':
        async with DatabaseContextManager() as session_methods:
            active_user_ids = await session_methods.subscription.get_active_subscribed_users()
        for user_id, user in users_dict.items():
            user['selected'] = user_id in active_user_ids
    elif callback_query.data == 'cancel_all':
        for user in users_dict.values():
            user['selected'] = False
    await state.update_data(users=users_dict)
    page = 1
    await show_users(callback_query.message, page, users_dict)
    await callback_query.answer()


@router.callback_query(UserPaginationCallback.filter())
async def paginate_users(callback_query: types.CallbackQuery, callback_data: UserPaginationCallback, state: FSMContext):
    data = await state.get_data()
    users_dict = data.get('users', {})
    page = callback_data.page
    if callback_data.action == 'next' and (page * 5) < len(users_dict):
        page += 1
        await show_users(callback_query.message, page, users_dict)
        return
    elif callback_data.action == 'previous' and page > 1:
        page -= 1
        await show_users(callback_query.message, page, users_dict)
        return
    await callback_query.answer()
    """Обработка нажатий на кнопки пагинации."""
    data = await state.get_data()
    users_dict = data.get('users', {})
    page = callback_data.page
    if callback_data.action == 'next' and page * 5 < len(users_dict) or callback_data.action == 'previous' and page > 1:
        await show_users(callback_query.message, page, users_dict)
    await callback_query.answer()


async def show_users(message: types.Message, page: int, users_dict: dict):
    users = list(users_dict.values())[5 * (page - 1):5 * page]
    has_next = len(users_dict) > page * 5

    keyboard = await InlineKeyboards.create_user_pagination_with_users_keyboard(users, page, has_next)

    user_list = "Кому отправим уведомления?"
    if not user_list:
        user_list = "No users found."

    # Отправляем сообщение с пользователями и клавиатурой
    try:
        await message.edit_text(user_list, reply_markup=keyboard)
    except Exception:
        await message.answer(user_list, reply_markup=keyboard)
