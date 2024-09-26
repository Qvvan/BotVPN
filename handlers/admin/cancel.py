from aiogram import Router, types
from aiogram.fsm.context import FSMContext

router = Router()


@router.callback_query(lambda c: c.data == 'cancel')
async def cancel_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()

    await state.clear()
