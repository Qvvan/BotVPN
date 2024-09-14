from datetime import datetime
from uuid import UUID

from aiogram import Router, F
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery

from database.db import DB
from keyboards.kb_inline import InlineKeyboards
from models.models import Transaction

router = Router()


async def send_invoice_handler(message: Message, price_service: int, service_name: str, service_id):
    prices = [LabeledPrice(label="XTR", amount=price_service)]
    await message.answer_invoice(
        title=f"VPN на {service_name}",
        description=f"Для оформления подписки, оплати {price_service} звезд по ссылке ниже.\n"
                    f"⬇️ После успешной оплаты, тебе будут высланы данные и инструкция для подключения VPN. 😎",
        prices=prices,
        provider_token="",
        payload=service_id,
        currency="XTR",
        reply_markup=InlineKeyboards.create_pay(price_service),
    )


@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    await message.bot.refund_star_payment(message.from_user.id,
                                          message.successful_payment.telegram_payment_charge_id)
    transaction_id = message.successful_payment.telegram_payment_charge_id
    tg_id = message.from_user.id
    service_id = message.successful_payment.invoice_payload
    status = 'successful'

    transaction = Transaction(
        transaction_id=transaction_id,
        service_id=service_id,
        tg_id=tg_id,
        status=status,
    )

    db_status = DB.get().add_transaction(transaction)
    if db_status:
        await message.answer("Оплата успешна! Данные о транзакции добавлены в базу.")
    else:
        await message.answer("Что-то пошло не так")


