from datetime import datetime, timedelta

from database.context_manager import DatabaseContextManager
from lexicon.lexicon_ru import LEXICON_RU
from main import logger
from models.models import Transactions, Subscriptions, VPNKeys
from outline.outline_manager.outline_manager import OutlineManager
from services.send_sms_admins import notify_group


async def process_successful_payment(message):
    await message.answer(text="Спасибо за покупку!")
    await refund_payment(message)

    async with DatabaseContextManager() as session_methods:
        try:
            logger.info("Transaction started for adding user and service.")
            manager = OutlineManager()
            await manager.wait_for_initialization()
            in_payload = message.successful_payment.invoice_payload.split(':')
            server_id = message.successful_payment.invoice_payload.split(':')[2]
            durations_days = in_payload[1]

            transaction_state = await create_transaction(message, 'successful', 'successful', session_methods)
            if not transaction_state:
                raise Exception("Ошибка сохранения транзакции")

            vpn_key = await session_methods.vpn_keys.get_vpn_key()
            if not vpn_key:
                raise Exception("Нет доступных ключей")

            await update_vpn_key(vpn_key.vpn_key_id, session_methods)
            subscription_created = await create_subscription(message, vpn_key.vpn_key_id, session_methods)

            if not subscription_created:
                raise Exception("Ошибка создания подписки")

            await manager.rename_key(server_id, vpn_key.outline_key_id, message.from_user.id)
            await send_success_response(message, vpn_key.key)
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


async def update_vpn_key(vpn_key_id: int, session_methods):
    vpn_key = VPNKeys(
        vpn_key_id=vpn_key_id,
        is_active=1,
    )
    await session_methods.vpn_keys.update_vpn_key(vpn_key)


async def create_subscription(message, vpn_key_id: int, session_methods) -> bool:
    in_payload = message.successful_payment.invoice_payload.split(':')
    service_id = int(in_payload[0])
    durations_days = in_payload[1]

    return await session_methods.subscription.create_sub(Subscriptions(
        user_id=message.from_user.id,
        service_id=service_id,
        vpn_key_id=vpn_key_id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=int(durations_days)),
    ))


async def send_success_response(message, vpn_key: str):
    await message.answer(text=LEXICON_RU['outline_info'])
    await message.answer(text=f'Ваш ключ: {vpn_key}')
