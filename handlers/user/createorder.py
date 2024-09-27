from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import InlineKeyboards, ServiceCallbackFactory, ServerCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger
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


@router.callback_query(ServerCallbackFactory.filter(), ChoiceServer.waiting_for_choice)
async def server_selected(callback_query: CallbackQuery, callback_data: ServerCallbackFactory, state: FSMContext):
    """Обрабатываем выбор сервера и создаем ключ."""
    server_id = callback_data.server_id
    count_key = callback_data.available_keys
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


@router.callback_query(ServiceCallbackFactory.filter(), ChoiceServer.waiting_for_services)
async def handle_service_callback(callback_query: CallbackQuery, callback_data: ServiceCallbackFactory,
                                  state: FSMContext):
    service_id = int(callback_data.service_id)
    server_id = callback_data.server_id

    await state.clear()

    await callback_query.message.delete()

    async with DatabaseContextManager() as session_methods:
        try:
            service = await session_methods.services.get_service_by_id(service_id)
            await send_invoice_handler(message=callback_query.message,
                                       price_service=service.price,
                                       service_name=service.name,
                                       service_id=service_id,
                                       duration_days=service.duration_days,
                                       server_id=server_id
                                       )
        except Exception as e:
            logger.error(f'Произошла ошибка: {e}')
            await callback_query.message.answer(text="Что-то пошло не так, обратитесь в техподдержку")


@router.callback_query(lambda c: c.data == 'back_to_servers', ChoiceServer.waiting_for_services)
async def server_selected(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.delete()
    await create_order(callback_query.message, state)


async def send_invoice_handler(message: Message, price_service: int, service_name: str, service_id: int,
                               duration_days: int,
                               server_id: str):
    try:
        prices = [LabeledPrice(label="XTR", amount=1)]  # price_service
        await message.answer_invoice(
            title=f"VPN на {service_name}",
            description=f"Для оформления подписки, оплати {price_service} звезд по ссылке ниже.\n"
                        f"⬇️ После успешной оплаты, тебе будут высланы данные и инструкция для подключения VPN. 😎",
            prices=prices,
            provider_token="",
            payload=f"{service_id}:{duration_days}:{server_id}",
            currency="XTR",
            reply_markup=await InlineKeyboards.create_pay(1),
        )
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        await message.answer(text="Что-то пошло не так, обратитесь в техподдержку")


@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    await process_successful_payment(message)