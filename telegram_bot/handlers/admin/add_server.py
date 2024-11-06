import ipaddress

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from keyboards.kb_inline import InlineKeyboards
from state.state import AddAdmin

router = Router()


# Команда для добавления сервера
@router.message(Command(commands='add_server'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(
        text='Отправьте IP-адрес сервера:',
        reply_markup=await InlineKeyboards.cancel()
    )
    await state.set_state(AddAdmin.waiting_ip)


@router.message(AddAdmin.waiting_ip)
async def process_server_ip(message: types.Message, state: FSMContext):
    server_ip = message.text

    try:
        ipaddress.ip_address(server_ip)

        await state.update_data(server_ip=server_ip)
        await message.answer("Отправьте имя сервера:")
        await state.set_state(AddAdmin.waiting_name)

    except ValueError:
        await message.answer("Ошибка: Некорректный формат IP-адреса. Пожалуйста, введите правильный IP-адрес.")


@router.message(AddAdmin.waiting_name)
async def process_server_name(message: types.Message, state: FSMContext):
    server_name = message.text

    await state.update_data(name=server_name)
    await message.answer("Отправьте лимит для сервера (например, 100):")
    await state.set_state(AddAdmin.waiting_limit)


@router.message(AddAdmin.waiting_limit)
async def process_server_limit(message: types.Message, state: FSMContext):
    try:
        limit = int(message.text)
    except ValueError:
        await message.answer("Ошибка: лимит должен быть числом.")
        return

    data = await state.get_data()
    server_ip = data.get('server_ip')
    name = data.get('name')
    SERVER = {
        "SERVER_IP": server_ip,
        "NAME": name,
        "LIMIT": limit
    }

    # Добавление сервера в базу данных
    async with DatabaseContextManager() as methods_session:
        try:
            await methods_session.servers.add_server(SERVER)
            await methods_session.session.commit()
            await message.answer("Сервер успешно добавлен.")
        except Exception as e:
            await message.answer(f'Не удалось добавить сервер:\n{e}')

    # Очистка состояния
    await state.clear()
