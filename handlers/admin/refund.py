from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from state.state import CancelTransaction

router = Router()


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
