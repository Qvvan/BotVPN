from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import InlineKeyboards, ServiceCallbackFactory, StatusPay
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from handlers.services.invoice_helper import send_invoice

router = Router()


@router.message(Command(commands='createorder'))
async def create_order(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON_RU['createorder'],
        reply_markup=await InlineKeyboards.create_order_keyboards(StatusPay.NEW)
    )

    await state.update_data(status_pay=StatusPay.NEW)


@router.callback_query(lambda c: c.data == 'subscribe')
async def handle_subscribe(callback: CallbackQuery):
    """Обработчик кнопки 'Оформить подписку' в главном меню."""
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON_RU['createorder'],
        reply_markup=await InlineKeyboards.create_order_keyboards(StatusPay.NEW)
    )


@router.callback_query(ServiceCallbackFactory.filter())
async def handle_service_callback(callback_query: CallbackQuery, callback_data: ServiceCallbackFactory):
    service_id = int(callback_data.service_id)
    status_pay = StatusPay(callback_data.status_pay)
    await callback_query.message.delete()

    async with DatabaseContextManager() as session_methods:
        try:
            service = await session_methods.services.get_service_by_id(service_id)
            await send_invoice(
                message=callback_query.message,
                price=service.price,
                description=f"Для оформления подписки, оплати {service.price} звезд по ссылке ниже.",
                service_name=service.name,
                service_id=service_id,
                duration_days=service.duration_days,
                action=status_pay.value
            )
        except Exception as e:
            await logger.log_error(f'Пользователь: @{callback_query.from_user.username}\n'
                                   f'ID: {callback_query.from_user.id}\n'
                                   f'При формирование кнопки оплаты произошла ошибка', e)
            await callback_query.message.edit_text(text="Что-то пошло не так, обратитесь в техподдержку")


@router.callback_query(lambda c: c.data == 'back_to_services')
async def back_to_services(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_data = await state.get_data()

    status_pay_value = user_data.get('status_pay', StatusPay.NEW.value)

    try:
        status_pay = StatusPay(status_pay_value)
    except ValueError:
        status_pay = StatusPay.NEW

    await callback.message.answer(
        text=LEXICON_RU['createorder'],
        reply_markup=await InlineKeyboards.create_order_keyboards(status_pay)
    )
    await callback.message.delete()
