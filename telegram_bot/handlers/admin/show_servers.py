from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import InlineKeyboards, ServerCallbackData
from logger.logging_config import logger
from state.state import ServerManagementStates
from utils.check_servers import is_server_reachable

router = Router()


@router.message(Command(commands="show_servers"))
async def show_servers_handler(message: types.Message, state: FSMContext):
    async with DatabaseContextManager() as session_methods:
        try:
            servers = await session_methods.servers.get_all_servers()
        except Exception as e:
            await logger.log_error("Не удалось получить список серверов", e)
            await message.answer("Произошла ошибка при получении списка серверов.")
            return

    for server in servers:
        reachable = await is_server_reachable(server.server_ip)
        status = "✅ Доступен" if reachable else "❌ Недоступен"
        hidden_status = "🟢 Включен" if server.hidden == 0 else "🔴 Выключен"

        text = (
            f"Название: {server.name} 📌\n"
            f"IP: {server.server_ip} 🌐\n"
            f"Статус: {status}\n"
            f"В БД: {hidden_status}"
        )

        await message.answer(text=text, reply_markup=await InlineKeyboards.server_management_options(server.server_ip,
                                                                                                     server.hidden))


@router.callback_query(ServerCallbackData.filter(F.action == "change_name"))
async def change_server_name_callback_handler(callback_query: types.CallbackQuery, callback_data: ServerCallbackData,
                                              state: FSMContext):
    server_ip = callback_data.server_ip

    await callback_query.message.answer(f"Введите новое имя для сервера с IP: {server_ip}")
    await state.update_data(server_ip=server_ip)
    await state.set_state(ServerManagementStates.waiting_for_name)


@router.message(ServerManagementStates.waiting_for_name)
async def receive_new_server_name(message: types.Message, state: FSMContext):
    new_name = message.text
    state_data = await state.get_data()
    server_ip = state_data['server_ip']

    async with DatabaseContextManager() as session_methods:
        try:
            await session_methods.servers.update_server(server_ip, name=new_name)
            await message.answer(f"Имя сервера с IP: {server_ip} успешно изменено на {new_name}.")
            await logger.info(f"Имя сервера {server_ip} было изменено на {new_name} администратором.")
        except Exception as e:
            await message.answer(f"Не удалось изменить имя сервера с IP: {server_ip}.")
            await logger.log_error(f"Ошибка при изменении имени сервера {server_ip}", e)

    await state.clear()


# Обработчик для изменения лимита сервера
@router.callback_query(ServerCallbackData.filter(F.action == "change_limit"))
async def change_server_limit_callback_handler(callback_query: types.CallbackQuery, callback_data: ServerCallbackData,
                                               state: FSMContext):
    server_ip = callback_data.server_ip

    await callback_query.message.answer(f"Введите новый лимит для сервера с IP: {server_ip}")
    await state.update_data(server_ip=server_ip)
    await state.set_state(ServerManagementStates.waiting_for_limit)


# Обработчик для получения нового лимита сервера
@router.message(ServerManagementStates.waiting_for_limit)
async def receive_new_server_limit(message: types.Message, state: FSMContext):
    try:
        new_limit = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное числовое значение для лимита.")
        return

    state_data = await state.get_data()
    server_ip = state_data['server_ip']

    async with DatabaseContextManager() as session_methods:
        try:
            await session_methods.servers.update_server(server_ip, limit=new_limit)
            await message.answer(f"Лимит сервера с IP: {server_ip} успешно изменен на {new_limit}.")
            await logger.info(f"Лимит сервера {server_ip} был изменен на {new_limit} администратором.")
        except Exception as e:
            await message.answer(f"Не удалось изменить лимит сервера с IP: {server_ip}.")
            await logger.log_error(f"Ошибка при изменении лимита сервера {server_ip}", e)

    await state.clear()


@router.callback_query(ServerCallbackData.filter(F.action == "disable"))
async def disable_server_callback_handler(callback_query: types.CallbackQuery, callback_data):
    server_ip = callback_data.server_ip
    async with DatabaseContextManager() as session_methods:
        try:
            await session_methods.servers.update_server(server_ip, hidden=1)
            await callback_query.answer(f"Сервер {server_ip} успешно выключен.", show_alert=True)
            await logger.info(f"Сервер {server_ip} был выключен администратором.")

            # Редактирование текста сообщения с обновленным статусом в БД
            updated_text = callback_query.message.text.replace("🟢 Включен", "🔴 Выключен")
            updated_keyboard = await InlineKeyboards.server_management_options(server_ip, hidden_status=1)
            await callback_query.message.edit_text(text=updated_text, reply_markup=updated_keyboard)

        except Exception as e:
            await callback_query.answer(f"Не удалось выключить сервер {server_ip}.", show_alert=True)
            await logger.log_error(f"Ошибка при выключении сервера {server_ip}", e)


@router.callback_query(ServerCallbackData.filter(F.action == "enable"))
async def enable_server_callback_handler(callback_query: types.CallbackQuery, callback_data):
    server_ip = callback_data.server_ip
    async with DatabaseContextManager() as session_methods:
        try:
            await session_methods.servers.update_server(server_ip, hidden=0)
            await callback_query.answer(f"Сервер {server_ip} успешно включен.", show_alert=True)
            await logger.info(f"Сервер {server_ip} был включен администратором.")

            # Редактирование текста сообщения с обновленным статусом в БД
            updated_text = callback_query.message.text.replace("🔴 Выключен", "🟢 Включен")
            updated_keyboard = await InlineKeyboards.server_management_options(server_ip, hidden_status=0)
            await callback_query.message.edit_text(text=updated_text, reply_markup=updated_keyboard)

        except Exception as e:
            await callback_query.answer(f"Не удалось включить сервер {server_ip}.", show_alert=True)
            await logger.log_error(f"Ошибка при включении сервера {server_ip}", e)
