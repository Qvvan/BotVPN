from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from state.state import KeyInfo

router = Router()

@router.message(Command(commands='key_info'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(text='Отправьте ключ, для получения полной информации')
    await state.set_state(KeyInfo.waiting_key_info)

@router.message(KeyInfo.waiting_key_info)
async def key_info(message: types.Message, state: FSMContext):
    key = message.text
    async with DatabaseContextManager() as session_methods:
        try:
            res = await session_methods.vpn_keys.key_info(key)
            if res["message"] == "Ключ используется":
                response_message = (
                    f"🔑 Информация о ключе:\n\n"
                    f"👤 Пользователь: @{res['username']}\n"
                    f"🆔 ID пользователя: {res['user_id']}\n\n"
                    f"📦 Название сервиса: {res['service_name']}\n\n"
                    f"📅 Начало подписки: {res['start_date']}\n"
                    f"📅 Конец подписки: {res['end_date']}\n\n"
                    f"🕒 Последнее обновление: {res['last_update']}\n"
                )
            else:
                response_message = "🔓 Ключ свободен!"

            await message.answer(response_message)
        except Exception as e:
            await message.answer(f"Произошла ошибка: \n{e}")

        await state.clear()