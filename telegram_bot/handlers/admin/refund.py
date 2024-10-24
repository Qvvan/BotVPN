from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
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
        result = await cancel_transaction(transaction_code, session_methods, message.bot)

        if result['success']:
            await message.answer("Транзакция успешно отменена!")
            await session_methods.session.commit()
        else:
            await message.answer(result['message'])

    await state.clear()


async def cancel_transaction(transaction_code: str, session, bot) -> dict:
    """
    Отменяет транзакцию по коду и выполняет возврат платежа.
    :param transaction_code: код транзакции для отмены
    :param session: сессия базы данных
    :param bot: экземпляр бота
    :return: dict с результатом операции
    """
    try:
        user_id, decrypted_transaction_code = await session.transactions.cancel_transaction(transaction_code)

        if user_id and decrypted_transaction_code:
            try:
                await bot.refund_star_payment(user_id, decrypted_transaction_code)
                await bot.send_message(chat_id=user_id, text=LEXICON_RU['refund_message'])
                return {'success': True, 'message': 'Транзакция успешно отменена!'}
            except Exception:
                return {'success': False, 'message': 'Транзакция уже отменена'}
        else:
            return {'success': False, 'message': 'Нет такой транзакции'}

    except Exception as e:
        logger.log_error('Не удалось отменить транзакцию', e)
        return {'success': False, 'message': f"Не удалось отменить транзакцию, ошибка:\n{str(e)}"}
