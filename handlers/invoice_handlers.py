import time
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery

from database.db import DB
from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from models.models import Transaction, Subscription, VPNKey

router = Router()


async def send_invoice_handler(message: Message, price_service: int, service_name: str, service_id, duration_days: str):
    prices = [LabeledPrice(label="XTR", amount=price_service)]
    await message.answer_invoice(
        title=f"VPN на {service_name}",
        description=f"Для оформления подписки, оплати {price_service} звезд по ссылке ниже.\n"
                    f"⬇️ После успешной оплаты, тебе будут высланы данные и инструкция для подключения VPN. 😎",
        prices=prices,
        provider_token="",
        payload=f"{service_id}:{duration_days}",
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
    in_payload = message.successful_payment.invoice_payload.split(':')
    service_id = int(in_payload[0])
    durations_days = int(in_payload[1])
    status = 'successful'

    transaction = Transaction(
        transaction_id=transaction_id,
        service_id=service_id,
        tg_id=tg_id,
        status=status,
    )

    state = DB.get().add_transaction(transaction)

    vpn_key = DB.get().get_vpn_key()
    if state:
        DB.get().update_vpn_key(VPNKey(
            is_active=1,
            is_blocked=0,
            id=vpn_key['id']

        ))

    create_sub = DB.get().create_sub(Subscription(
        tg_id=tg_id,
        service_id=service_id,
        vpn_key_id=vpn_key['key'],
        start_date=time.time(),
        end_date=(datetime.now() + timedelta(days=int(durations_days))).timestamp(),
    ))
    if create_sub:
        await message.answer(text=LEXICON_RU['outline_info'])
        await message.answer(text=f'Ваш ключ: {vpn_key['key']}')
