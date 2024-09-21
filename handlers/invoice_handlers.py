from aiogram import Router, F
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery

from keyboards.kb_inline import InlineKeyboards
from services.services import process_successful_payment

router = Router()


async def send_invoice_handler(message: Message, price_service: int, service_name: str, service_id, duration_days: str, server_id: str):
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
