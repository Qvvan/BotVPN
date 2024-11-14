import ipaddress

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from keyboards.kb_inline import InlineKeyboards, SubscriptionCallbackFactory
from state.state import AddAdmin

router = Router()


@router.message(Command(commands='active'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message):
    async with DatabaseContextManager() as session_methods:
        try:
            users = await session_methods.subscription.get_active_subscribed_users()
            count_users = len(users)
            await message.answer(
                text=f"Активные пользователи: {count_users}",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Список всех",
                                callback_data="show_all_users"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="Отмена",
                                callback_data="cancel"
                            )
                        ],
                    ]
                ),
            )
        except Exception as error:
            await message.answer(f"Произошла ошибка: {error}")


@router.callback_query(lambda c: c.data == 'show_all_users')
async def cancel_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        text="TODO: Тут можно будет узнать список всех пользователей",
        reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Назад",
                                callback_data="active"
                            )
                        ],
                    ]
            )
    )
