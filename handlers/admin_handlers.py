from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config_data.config import ADMIN_IDS
from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_COMMANDS_ADMIN, LEXICON_RU
from outline.outline_manager.outline_manager import OutlineManager
from state.state import AddKeyStates, CancelTransaction

router = Router()


@router.message(Command(commands="add_key"), IsAdmin(ADMIN_IDS))
async def add_key_command(message: types.Message, state: FSMContext):
    """Вывод клавиатуры для выбора сервера."""
    await message.answer(
        text="Выберите сервер для создания нового VPN ключа:",
        reply_markup=await InlineKeyboards.server_selection_keyboards()
    )
    await state.set_state(AddKeyStates.waiting_for_server)


@router.callback_query(lambda c: c.data.startswith("select_server:"), AddKeyStates.waiting_for_server)
async def server_selected(call: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор сервера и создаем ключ."""
    manager = OutlineManager()  # Инициализация менеджера
    await manager.wait_for_initialization()
    server_id = int(call.data.split(":")[1])

    servers = await manager.list_servers()
    server_name = servers.get(server_id)

    if server_name is None:
        await call.message.answer("Сервер не найден.")
        return

    async with DatabaseContextManager() as session_methods:
        try:
            outline_key = await manager.create_key(server_id=server_id)

            await session_methods.vpn_keys.add_vpn_key(outline_key.access_url, server_name, outline_key.key_id)
            await session_methods.session.commit()

            await call.message.answer(
                f"Ключ: \n{outline_key.access_url} \nУспешно создан и добавлен на сервер: {server_name}"
            )
        except Exception as e:
            await call.message.answer(f'Не удалось создать ключ, ошибка:\n{e}')

        await state.clear()


@router.message(Command(commands="refund"))
async def start_another_feature(message: types.Message, state: FSMContext):
    await message.answer(
        text="Введите код транзакции",
        reply_markup=await InlineKeyboards.cancel()
    )
    await state.set_state(CancelTransaction.waiting_for_transaction)


@router.message(CancelTransaction.waiting_for_transaction)
async def process_another_input(message: types.Message, state: FSMContext):
    transaction_code = message.text
    async with DatabaseContextManager() as session_methods:
        try:
            user_id, decrypted_transaction_code = await session_methods.transactions.cancel_transaction(
                transaction_code)
            if user_id and decrypted_transaction_code:
                try:
                    await message.bot.refund_star_payment(user_id, decrypted_transaction_code)
                    await message.answer(f"Транзакция успешно отменена!")
                    await message.bot.send_message(chat_id=user_id, text=LEXICON_RU['refund_message'])
                    await session_methods.session.commit()
                except:
                    await message.answer(text='Транзакция уже отменена')
            else:
                raise "Нет такой транзакции"
        except Exception as e:
            await message.answer(f"Не удалось отменить транзакцию, ошибка:\n{e}")
        await state.clear()


@router.message(Command(commands='help'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message):
    ans = ''
    for command, description in LEXICON_COMMANDS_ADMIN.items():
        ans += f'{command}: {description}\n'
    await message.answer(ans)


@router.callback_query(lambda c: c.data == 'cancel')
async def cancel_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    await state.clear()
