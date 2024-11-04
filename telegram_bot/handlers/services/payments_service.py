from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import PreCheckoutQuery

from handlers.services.subscriptions_service import SubscriptionsService

router = Router()


@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):
    payload = message.successful_payment.invoice_payload
    _, _, action, *rest = payload.split(':')
    if action == 'new':
        await SubscriptionsService.process_new_subscription(message)
    elif action == 'old':
        await SubscriptionsService.extend_sub_successful_payment(message, state)
