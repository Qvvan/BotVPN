from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice

from database.context_manager import DatabaseContextManager
from handlers.user.subs import extend_sub_successful_payment, new_order_successful_payment
from keyboards.kb_inline import InlineKeyboards, ServiceCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
from services.send_sms_admins import notify_group
from services.services import process_successful_payment
from state.state import ChoiceServer

router = Router()


@router.message(Command(commands='createorder'))
async def create_order(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON_RU['createorder'],
        reply_markup=await InlineKeyboards.create_order_keyboards()
    )

    await state.set_state(ChoiceServer.waiting_for_services)


@router.callback_query(ServiceCallbackFactory.filter(), ChoiceServer.waiting_for_services)
async def handle_service_callback(callback_query: CallbackQuery, callback_data: ServiceCallbackFactory):
    service_id = int(callback_data.service_id)
    await callback_query.message.delete()

    async with DatabaseContextManager() as session_methods:
        try:
            service = await session_methods.services.get_service_by_id(service_id)
            await send_invoice_handler(message=callback_query.message,
                                       price_service=service.price,
                                       service_name=service.name,
                                       service_id=service_id,
                                       duration_days=service.duration_days
                                       )
        except Exception as e:
            logger.error(f'Произошла ошибка: {e}')
            await callback_query.message.edit_text(text="Что-то пошло не так, обратитесь в техподдержку")
            await notify_group(
                message=f'Пользователь: @{callback_query.message.from_user.username}\n'
                        f'ID: {callback_query.message.from_user.id}\n'
                        f'Произошла ошибка при формировании оплаты\n{e}\n\n'
                        f'#оплата',
                is_error=True
            )


@router.callback_query(lambda c: c.data == 'back_to_servers', ChoiceServer.waiting_for_services)
async def server_selected(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text(
        text='Выберите подходящий для вас сервер.',
        reply_markup=await InlineKeyboards.server_selection_keyboards(),
        parse_mode=ParseMode.MARKDOWN,
    )
    await state.set_state(ChoiceServer.waiting_for_choice)


@router.callback_query(lambda c: c.data == 'back_to_services')
async def back_to_services(callback_query: CallbackQuery, state: FSMContext):
    """Возврат к выбору сервиса."""
    data = await state.get_data()
    server_id = data.get('server_id')

    await callback_query.message.answer(
        text=LEXICON_RU['createorder'],
        reply_markup=await InlineKeyboards.create_order_keyboards()
    )
    await callback_query.message.delete()


async def send_invoice_handler(message: Message, price_service: int, service_name: str, service_id: int,
                               duration_days: int,):
    try:
        prices = [LabeledPrice(label="XTR", amount=price_service)]
        await message.answer_invoice(
            title=f"VPN на {service_name}",
            description=f"Для оформления подписки, оплати {price_service} звезд по ссылке ниже.\n"
                        f"⬇️ После успешной оплаты, тебе будут высланы данные и инструкция для подключения VPN. 😎",
            prices=prices,
            provider_token="",
            payload=f"{service_id}:{duration_days}:new",
            currency="XTR",
            reply_markup=await InlineKeyboards.create_pay(price_service),
        )
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        await message.answer(text="Что-то пошло не так, обратитесь в техподдержку")


@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    service_id, duration_days, action = payload.split(':')
    if action == 'new':
        await process_successful_payment(message)
    elif action == 'old':
        await extend_sub_successful_payment(message)
    elif action == 'extend':
        await new_order_successful_payment(message)
