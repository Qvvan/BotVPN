import json

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from outline_vpn.outline_vpn import OutlineVPN

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
        text='Отправьте JSON-сообщение с данными о сервере (apiUrl и certSha256):',
        reply_markup=await InlineKeyboards.cancel()
    )
    await state.set_state(AddAdmin.waiting_json)


# Обработка JSON-сообщения
@router.message(AddAdmin.waiting_json)
async def process_server_json(message: types.Message, state: FSMContext):
    json_message = message.text

    try:
        # Парсим JSON-данные из текста
        data = json.loads(json_message)
        apiUrl = data.get("apiUrl")
        certSha256 = data.get("certSha256")

        if not apiUrl or not certSha256:
            await message.answer("Ошибка: JSON должен содержать оба поля `apiUrl` и `certSha256`.")
            await state.clear()
            return

        # Сохранение данных в состоянии
        await state.update_data(apiUrl=apiUrl, certSha256=certSha256)

        # Запрос лимита
        await message.answer("Отправьте лимит для сервера (например, 100):")
        await state.set_state(AddAdmin.waiting_limit)

    except json.JSONDecodeError:
        await message.answer("Ошибка: Некорректный формат JSON. Пожалуйста, отправьте правильное JSON-сообщение.")


# Обработка лимита
@router.message(AddAdmin.waiting_limit)
async def process_server_limit(message: types.Message, state: FSMContext):
    try:
        limit = int(message.text)
    except ValueError:
        await message.answer("Ошибка: лимит должен быть числом.")
        return

    data = await state.get_data()
    apiUrl = data.get('apiUrl')
    certSha256 = data.get('certSha256')

    # Подключение к серверу
    try:
        client = OutlineVPN(api_url=apiUrl, cert_sha256=certSha256)
        server_info = client.get_server_information()
    except Exception as e:
        await message.answer(f"Ошибка при соединении с сервером:\n{e}")
        await state.clear()
        return

    # Формируем данные для добавления в базу
    SERVER = {
        "SERVER_ID": server_info['serverId'],
        "NAME": server_info['name'],
        "CERT_SHA256": certSha256,
        "API_URL": apiUrl,
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
