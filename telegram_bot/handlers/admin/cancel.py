from aiogram import Router, types
from aiogram.fsm.context import FSMContext

router = Router()


@router.callback_query(lambda c: c.data == 'cancel')
async def cancel_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()

    await state.clear()
