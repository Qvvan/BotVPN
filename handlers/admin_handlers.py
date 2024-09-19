from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.context_manager import DatabaseContextManager
from filters.admin import IsAdmin
from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_COMMANDS_ADMIN
from state.state import AddKeyStates, AnotherFeatureStates
from config_data.config import ADMIN_IDS

router = Router()


@router.message(Command(commands="add_key"), IsAdmin(ADMIN_IDS))
async def add_key_command(message: types.Message, state: FSMContext):
    await message.answer(
        text="Введите новый VPN ключ",
        reply_markup=await InlineKeyboards.cancel()
    )
    await state.set_state(AddKeyStates.waiting_for_key)


@router.message(AddKeyStates.waiting_for_key)
async def process_key(message: types.Message, state: FSMContext):
    key = message.text
    async with DatabaseContextManager() as session_methods:
        try:
            await session_methods.vpn_keys.add_vpn_key(key)
            await message.answer(f"Ключ {key} успешно добавлен!")
            await session_methods.session.commit()
            await state.clear()
        except Exception as e:
            await message.answer(f'Не удалось добавить ключ, ошибка:\n{e}')


@router.callback_query(lambda c: c.data == 'cancel')
async def cancel_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    await state.clear()

    await callback_query.message.answer("Действие отменено.")


# Обработчики для AnotherFeatureStates
@router.message(Command(commands="another_command"))
async def start_another_feature(message: types.Message, state: FSMContext):
    await message.answer("Введите данные для новой функции:")
    await state.set_state(AnotherFeatureStates.waiting_for_input)


@router.message(AnotherFeatureStates.waiting_for_input)
async def process_another_input(message: types.Message, state: FSMContext):
    input_data = message.text
    # Логика для обработки данных
    await message.answer(f"Вы ввели: {input_data}")
    await state.set_state(AnotherFeatureStates.processing)


@router.message(AnotherFeatureStates.processing)
async def finish_another_feature(message: types.Message, state: FSMContext):
    # Логика завершения обработки
    await message.answer("Обработка завершена.")
    await state.clear()


@router.message(Command(commands='help'), IsAdmin(ADMIN_IDS))
async def show_commands(message: types.Message):
    ans = ''
    for command, description in LEXICON_COMMANDS_ADMIN.items():
        ans += f'{command}: {description}\n'
    await message.answer(ans)

