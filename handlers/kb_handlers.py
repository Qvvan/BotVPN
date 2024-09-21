from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from handlers.invoice_handlers import send_invoice_handler
from handlers.user_handlers import create_order
from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from state.state import ChoiceServer

router = Router()


@router.callback_query(lambda c: c.data.startswith('service'), ChoiceServer.waiting_for_services)
async def handle_service_callback(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data.split(':')
    service_id = data[1]
    price_service = int(float(1))
    service_name = data[3]
    duration_days = data[4]
    server_id = data[5]

    await state.clear()

    await callback_query.message.delete()

    await send_invoice_handler(message=callback_query.message,
                               price_service=price_service,
                               service_name=service_name,
                               service_id=service_id,
                               duration_days=duration_days,
                               server_id=server_id
                               )


@router.callback_query(lambda c: c.data.startswith("select_server:"), ChoiceServer.waiting_for_choice)
async def server_selected(callback_query: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор сервера и создаем ключ."""
    callback_data = callback_query.data.split(':')
    server_id = callback_data[1]
    count_key = int(callback_data[2])
    if count_key == 0:
        await callback_query.answer(
            text='К сожалению, на данном сервере нет доступных ключей.\n'
                 'Пожалуйста, выбери другой сервер или обратись в техподдержку для получения помощи.',
            show_alert=True  # This will display it as a notification
        )
        return
    await callback_query.message.delete()

    await callback_query.message.answer(
        text=LEXICON_RU['createorder'],
        reply_markup=await InlineKeyboards.create_order_keyboards(server_id)
    )

    await state.set_state(ChoiceServer.waiting_for_services)


@router.callback_query(lambda c: c.data == 'back_to_servers', ChoiceServer.waiting_for_services)
async def server_selected(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.delete()
    await create_order(callback_query.message, state)
