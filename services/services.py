import time
from datetime import datetime, timedelta
from database.db import DB
from models.models import Transactions, Subscriptions, VPNKeys
from lexicon.lexicon_ru import LEXICON_RU


async def process_successful_payment(message):
    await message.answer(text="Спасибо за покупку!")

    transaction = create_transaction(message, 'succesful')
    transaction_state = DB.get().transactions.add_transaction(transaction)
    await refund_payment(message)

    vpn_key = DB.get().vpn_keys.get_vpn_key()
    if vpn_key:
        if transaction_state:
            update_vpn_key(str(vpn_key['id']))
            subscription_created = create_subscription(message, vpn_key['key'])
            if subscription_created:
                await send_success_response(message, vpn_key['key'])
            else:
                await message.answer(text="Не удалось создать подписку. Попробуйте позже.")
                transaction = create_transaction(message, 'отмена: создание подписки')
                DB.get().transactions.add_transaction(transaction)
                await refund_payment(message)
        else:
            await message.answer(text="Не удалось сохранить транзакцию. Попробуйте позже.")
            transaction = create_transaction(message, 'отмена транзакции')
            DB.get().transactions.add_transaction(transaction)
            await refund_payment(message)
    else:
        await message.answer(text="К сожалению, ключи закончились, обратитесь в тех. поддержку")
        transaction = create_transaction(message, 'отмена: нет ключей')
        DB.get().transactions.add_transaction(transaction)
        await refund_payment(message)


async def refund_payment(message):
    await message.bot.refund_star_payment(message.from_user.id, message.successful_payment.telegram_payment_charge_id)


def create_transaction(message, status) -> Transactions:
    in_payload = message.successful_payment.invoice_payload.split(':')
    return Transactions(
        transaction_id=message.successful_payment.telegram_payment_charge_id,
        service_id=in_payload[0],
        tg_id=str(message.from_user.id),
        status=status
    )


def update_vpn_key(vpn_key_id: str):
    DB.get().vpn_keys.update_vpn_key(VPNKeys(
        id=vpn_key_id,
        is_active=1,
        is_blocked=0,
    ))


def create_subscription(message, vpn_key: str) -> bool:
    in_payload = message.successful_payment.invoice_payload.split(':')
    service_id = in_payload[0]
    durations_days = in_payload[1]

    return DB.get().subscriptions.create_sub(Subscriptions(
        tg_id=str(message.from_user.id),
        service_id=service_id,
        vpn_key_id=vpn_key,
        start_date=time.time(),
        end_date=(datetime.now() + timedelta(days=int(durations_days))).timestamp(),
    ))


async def send_success_response(message, vpn_key: str):
    await message.answer(text=LEXICON_RU['outline_info'])
    await message.answer(text=f'Ваш ключ: {vpn_key}')
