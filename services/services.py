import time
from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError

from database.db import DB
from models.models import Transactions, Subscriptions, VPNKeys
from lexicon.lexicon_ru import LEXICON_RU


async def process_successful_payment(message):
    await refund_payment(message)

    connection = DB.get().connection
    print('Hello')
    try:
        print('Я тут')
        async with connection.begin():
            print('И тут тоже')
            await message.answer(text="Спасибо за покупку!")

            transaction_state = create_transaction(message, 'successful')

            vpn_key = await DB.get().vpn_keys.get_vpn_key(connection)
            if vpn_key:
                if transaction_state:
                    await update_vpn_key(str(vpn_key['id']), connection)
                    subscription_created = await create_subscription(message, vpn_key['key'], connection)
                    if subscription_created:
                        await send_success_response(message, vpn_key['key'])
                    else:
                        await message.answer(text="Не удалось создать подписку. Попробуйте позже.")
                        raise Exception("Ошибка создания подписки")
                else:
                    # Если не удалось сохранить транзакцию
                    await message.answer(text="Не удалось сохранить транзакцию. Попробуйте позже.")
                    raise Exception("Ошибка сохранения транзакции")
            else:
                # Если ключи закончились
                await message.answer(text="К сожалению, ключи закончились, обратитесь в тех. поддержку")
                raise Exception("Нет доступных ключей")

    except SQLAlchemyError as e:
        await refund_payment(message)
        create_transaction(message, status=str(e))

async def refund_payment(message):
    await message.bot.refund_star_payment(message.from_user.id, message.successful_payment.telegram_payment_charge_id)

def create_transaction(message, status: str) -> Transactions:
    in_payload = message.successful_payment.invoice_payload.split(':')

    transaction_code = message.successful_payment.telegram_payment_charge_id
    service_id = int(in_payload[0])
    user_id = message.from_user.id

    # Создание транзакции
    transaction = DB.get().transactions.create_transaction(
        transaction_code=transaction_code,
        service_id=service_id,
        user_id=user_id,
        status=status
    )

    return transaction

async def update_vpn_key(vpn_key_id: str, connection):
    await DB.get().vpn_keys.update_vpn_key(VPNKeys(
        id=vpn_key_id,
        is_active=1,
        is_blocked=0,
    ), connection)

async def create_subscription(message, vpn_key: str, connection) -> bool:
    in_payload = message.successful_payment.invoice_payload.split(':')
    service_id = in_payload[0]
    durations_days = in_payload[1]

    return await DB.get().subscriptions.create_sub(Subscriptions(
        tg_id=str(message.from_user.id),
        service_id=service_id,
        vpn_key_id=vpn_key,
        start_date=time.time(),
        end_date=(datetime.now() + timedelta(days=int(durations_days))).timestamp(),
    ), connection)

async def send_success_response(message, vpn_key: str):
    await message.answer(text=LEXICON_RU['outline_info'])
    await message.answer(text=f'Ваш ключ: {vpn_key}')