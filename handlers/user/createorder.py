from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice

from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from services.services import process_successful_payment
from state.state import ChoiceServer

router = Router()


@router.message(Command(commands='createorder'))
async def create_order(message: Message, state: FSMContext):
    await message.answer(
        text='Выберите подходящий для вас сервер.',
        reply_markup=await InlineKeyboards.server_selection_keyboards(),
        parse_mode=ParseMode.MARKDOWN,
    )
    await state.set_state(ChoiceServer.waiting_for_choice)


@router.callback_query(lambda c: c.data.startswith("select_server:"), ChoiceServer.waiting_for_choice)
async def server_selected(callback_query: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор сервера и создаем ключ."""
    callback_data = callback_query.data.split(':')
    server_id = callback_data[1]
    count_key = int(callback_data[2])
    if count_key == 0:
        await callback_query.answer(
            text='К сожалению, на данном сервере нет доступных ключей.\n'
                 'Пожалуйста, выбери другой сервер или обратись в техподдержку для получения помощи.',
            show_alert=True
        )
        return
    await callback_query.message.delete()

    await callback_query.message.answer(
        text=LEXICON_RU['createorder'],
        reply_markup=await InlineKeyboards.create_order_keyboards(server_id)
    )

    await state.set_state(ChoiceServer.waiting_for_services)


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


@router.callback_query(lambda c: c.data == 'back_to_servers', ChoiceServer.waiting_for_services)
async def server_selected(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.delete()
    await create_order(callback_query.message, state)


async def send_invoice_handler(message: Message, price_service: int, service_name: str, service_id, duration_days: str,
                               server_id: str):
    prices = [LabeledPrice(label="XTR", amount=price_service)]
    await message.answer_invoice(
        title=f"VPN на {service_name}",
        description=f"Для оформления подписки, оплати {price_service} звезд по ссылке ниже.\n"
                    f"⬇️ После успешной оплаты, тебе будут высланы данные и инструкция для подключения VPN. 😎",
        prices=prices,
        provider_token="",
        payload=f"{service_id}:{duration_days}:{server_id}",
        currency="XTR",
        reply_markup=await InlineKeyboards.create_pay(price_service),
    )


@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    await process_successful_payment(message)
