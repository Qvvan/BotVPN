from aiogram import Router
from aiogram.types import CallbackQuery

from handlers.invoice_handlers import send_invoice_handler

router = Router()


@router.callback_query()
async def handle_service_callback(callback_query: CallbackQuery):
    data = callback_query.data.split(':')
    service_id = data[1]
    service_name = data[3]
    price_service = int(float(1))

    await send_invoice_handler(message=callback_query.message,
                               price_service=price_service,
                               service_name=service_name,
                               service_id=service_id,
                               )
