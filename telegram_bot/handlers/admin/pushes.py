from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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


@router.callback_query(lambda call: call.data == 'save')
async def handle_save_button(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    users_dict = data.get('users', {})
    selected_users = [user for user in users_dict.values() if user['selected']]
    if not selected_users:
        await callback_query.answer("Не выбрано ни одного пользователя", show_alert=True)
        return
    await state.update_data(selected_users=selected_users)
    await callback_query.message.edit_text("Напишите текст для уведомления")
    await state.set_state("waiting_for_message_text")

@router.message(StateFilter("waiting_for_message_text"))
async def handle_message_text(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, введите текст для уведомления.")
        return

    await state.update_data(message_text=message.text)
    data = await state.get_data()
    selected_users = data.get('selected_users', [])

    await message.answer(
        f"Текст уведомления сохранен\n\n{message.text}\n\nКоличество получателей: {len(selected_users)}.",
        reply_markup=await InlineKeyboards.show_notify_change_cancel()
    )
    await state.set_state(None)

@router.callback_query(lambda call: call.data == 'edit_message')
async def edit_message(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Напишите новый текст для уведомления")
    await state.set_state("waiting_for_message_text")


@router.callback_query(lambda call: call.data == 'send_notification')
async def send_notification(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_text = data.get('message_text')
    selected_users = data.get('selected_users', [])

    if not message_text:
        await callback_query.answer("Текст уведомления отсутствует. Пожалуйста, задайте текст перед отправкой.", show_alert=True)
        return

    count = 0
    for user in selected_users:
        try:
            await callback_query.bot.send_message(chat_id=user['user_id'], text=message_text)
            count += 1
        except Exception as e:
            await callback_query.message.answer(f"Ошибка при отправке пользователю {user['user_id']}: {e}")

    await callback_query.answer(f"Уведомление отправлено {count} пользователям.", show_alert=True, cache_time=2)

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
