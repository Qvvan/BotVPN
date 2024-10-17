from datetime import datetime, timedelta

from telegram_bot.config_data.config import OUTLINE_USERS_GATEWAY, OUTLINE_SALT
from telegram_bot.database.context_manager import DatabaseContextManager
from telegram_bot.lexicon.lexicon_ru import LEXICON_RU
from telegram_bot.main import logger
from telegram_bot.models.models import Transactions, Subscriptions
from telegram_bot.outline.outline_manager.outline_manager import OutlineManager
from telegram_bot.services.crypto import encrypt_part
from telegram_bot.services.send_sms_admins import notify_group


async def process_successful_payment(message):
    await message.answer(text=LEXICON_RU['purchase_thank_you'])

    async with DatabaseContextManager() as session_methods:
        try:
            logger.info("Transaction started for adding user and service.")
            manager = OutlineManager()
            await manager.wait_for_initialization()
            in_payload = message.successful_payment.invoice_payload.split(':')
            durations_days = in_payload[1]
            user_id = message.from_user.id

            transaction_state = await create_transaction(message, 'successful', 'successful', session_methods)
            if not transaction_state:
                raise Exception("Ошибка сохранения транзакции")

            part_to_encrypt = f"{OUTLINE_SALT}{hex(int(user_id))[2:]}"
            encrypted_part = encrypt_part(part_to_encrypt)
            dynamic_key = f"{OUTLINE_USERS_GATEWAY}/access-key/{encrypted_part}#VPN"

            subscription_created = await create_subscription(message, dynamic_key, session_methods)
            if not subscription_created:
                raise Exception("Ошибка создания подписки")

            await send_success_response(message, dynamic_key)
            await session_methods.session.commit()
            await notify_group(
                message=f'Пользователь: @{message.from_user.username}\n'
                        f'ID: {message.from_user.id}\n'
                        f'Оформил новую подписку: {durations_days} дней\n'
                        f'#подписка'
            )

        except Exception as e:
            logger.error(f"Error during transaction processing: {e}")
            await message.answer(text=f"К сожалению, покупка отменена.\nОбратитесь в техподдержку.")
            await refund_payment(message)

            await session_methods.session.rollback()

            await create_transaction(message, status='отмена', description=str(e), session_methods=session_methods)
            await session_methods.session.commit()
            await notify_group(
                message=f'Пользователь: @{message.from_user.username}\n'
                        f'ID: {message.from_user.id}\n'
                        f'Пытался оформить подписку:\n{e}\n\n'
                        f'#подписка'
            )


async def create_transaction(message, status, description: str, session_methods) -> Transactions:
    in_payload = message.successful_payment.invoice_payload.split(':')

    transaction_code = message.successful_payment.telegram_payment_charge_id
    service_id = int(in_payload[0])
    user_id = message.from_user.id

    transaction = await session_methods.transactions.add_transaction(
        transaction_code=transaction_code,
        service_id=service_id,
        user_id=user_id,
        status=status,
        description=description,
    )

    return transaction


async def refund_payment(message):
    await message.bot.refund_star_payment(message.from_user.id, message.successful_payment.telegram_payment_charge_id)


async def create_subscription(message, dynamic_key: str, session_methods) -> bool:
    in_payload = message.successful_payment.invoice_payload.split(':')
    service_id = int(in_payload[0])
    durations_days = in_payload[1]

    return await session_methods.subscription.create_sub(Subscriptions(
        user_id=message.from_user.id,
        service_id=service_id,
        dynamic_key=dynamic_key,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=int(durations_days)),
    ))


async def send_success_response(message, vpn_key: str):
    await message.answer(text=LEXICON_RU['outline_info'])
    await message.answer(
        text=f'Ваш ключ:\n<pre>{vpn_key}</pre>',
        parse_mode="HTML",
        )
