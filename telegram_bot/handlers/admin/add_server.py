from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from outline_vpn.outline_vpn import OutlineVPN

from telegram_bot.config_data.config import ADMIN_IDS
from telegram_bot.database.context_manager import DatabaseContextManager
from telegram_bot.filters.admin import IsAdmin
from telegram_bot.keyboards.kb_inline import InlineKeyboards
from telegram_bot.state.state import AddAdmin

router = Router()


@router.message(Command(commands='add_server'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message, state: FSMContext):
    await message.answer(
        text='Отправь apiUrl:',
        reply_markup=await InlineKeyboards.cancel()
        )
    await state.set_state(AddAdmin.waiting_apiUrl)


@router.message(AddAdmin.waiting_apiUrl)
async def process_api_url(message: types.Message, state: FSMContext):
    apiUrl = message.text
    await state.update_data(apiUrl=apiUrl)
    await message.answer(text='Отправьте certSha256:')
    await state.set_state(AddAdmin.waiting_certSha256)


@router.message(AddAdmin.waiting_certSha256)
async def process_cert_sha256(message: types.Message, state: FSMContext):
    certSha256 = message.text
    data = await state.get_data()
    apiUrl = data.get('apiUrl')
    server_info = None

    try:
        client = OutlineVPN(api_url=apiUrl, cert_sha256=certSha256)
        server_info = client.get_server_information()
    except Exception as e:
        await message.answer(f"Ошибка при соединении с сервером:\n{e}")
        await state.clear()
        return

    SERVER = {
        "SERVER_ID": server_info['serverId'],
        "NAME": server_info['name'],
        "CERT_SHA256": certSha256,
        "API_URL": apiUrl,
    }

    async with DatabaseContextManager() as methods_session:
        try:
            await methods_session.servers.add_server(SERVER)
            await methods_session.session.commit()
            await message.answer("Сервер успешно добавлен.")
        except Exception as e:
            await message.answer(f'Не удалось добавить сервер:\n{e}')

    await state.clear()
