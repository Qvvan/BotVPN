from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from keyboards.kb_inline import InlineKeyboards
from outline.outline_manager.outline_manager import OutlineManager
from state.state import AddKeyStates

router = Router()


@router.message(Command(commands="add_key"), IsAdmin(ADMIN_IDS))
async def add_key_command(message: types.Message, state: FSMContext):
    """Вывод клавиатуры для выбора сервера."""
    await message.answer(
        text="Выберите сервер для создания нового VPN ключа:",
        reply_markup=await InlineKeyboards.server_selection_keyboards(not_show_server=False)
    )
    await state.set_state(AddKeyStates.waiting_for_server)


@router.callback_query(lambda c: c.data.startswith("select_server:"), AddKeyStates.waiting_for_server)
async def server_selected(call: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор сервера и создаем ключ."""
    manager = OutlineManager()
    await manager.wait_for_initialization()
    server_id = call.data.split(":")[1]

    servers = await manager.list_servers()
    server_name = servers.get(server_id)

    if server_name is None:
        await call.message.answer("Сервер не найден.")
        return

    async with DatabaseContextManager() as session_methods:
        try:
            outline_key = await manager.create_key(server_id=server_id)

            await session_methods.vpn_keys.add_vpn_key(outline_key.access_url, server_name, outline_key.key_id, server_id)
            await session_methods.session.commit()

            await call.message.answer(
                f"Ключ: \n{outline_key.access_url} \nУспешно создан и добавлен на сервер: {server_name}"
            )
        except Exception as e:
            await call.message.answer(f'Не удалось создать ключ, ошибка:\n{e}')

