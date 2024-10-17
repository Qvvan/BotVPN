from datetime import datetime, timedelta
from typing import Any

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LabeledPrice

from telegram_bot.database.context_manager import DatabaseContextManager
from telegram_bot.keyboards.kb_inline import InlineKeyboards, SubscriptionCallbackFactory
from telegram_bot.lexicon.lexicon_ru import LEXICON_RU
from telegram_bot.logger.logging_config import logger
from telegram_bot.models.models import Subscriptions, SubscriptionStatusEnum
from telegram_bot.outline.outline_manager.outline_manager import OutlineManager
from telegram_bot.services.send_sms_admins import notify_group

router = Router()


@router.message(Command(commands='subs'))
async def get_user_subs(message: Message):
    user_id = message.from_user.id
    async with DatabaseContextManager() as session:
        try:
            subscription_data = await session.subscription.get_subscription(user_id)
            if subscription_data is None:
                await message.answer(text=LEXICON_RU['not_exists'])
                return
            for data in subscription_data:
                start_date = data.start_date
                end_date = data.end_date
                dynamic_key = data.dynamic_key
                service_name = data.name
                status = data.status


                parseSubs = (
                    f"📶 Статус: {'🟢 Активна' if status == 'активная' else '🔴 Истекла'}\n"
                    f"💼 Услуга: {service_name}\n\n"
                    f"📆 Дата начала: {start_date.strftime('%Y-%m-%d')}\n"
                    f"📆 Дата окончания: {end_date.strftime('%Y-%m-%d')}\n\n"
                    f"🔑 Ключ:\n"
                    f"<pre>{dynamic_key}</pre>"
                )

                if status == 'истекла':
                    keyboard = await InlineKeyboards.extend_subscription(data.subscription_id)
                    await message.answer(
                        text=parseSubs,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                else:
                    await message.answer(text=parseSubs, parse_mode="HTML")

        except Exception as e:
            logger.error('Ошибка при получении подписок', e)
            await notify_group(
                message=f'Ошибка при получении подписок у пользователя:\n{message.from_user.id}\n{message.from_user.username}',
                is_error=True)


@router.callback_query(SubscriptionCallbackFactory.filter(F.action == 'extend_subscription'))
async def extend_subscription(callback: CallbackQuery, callback_data: SubscriptionCallbackFactory):
    subscription_id = callback_data.subscription_id

    keyboard = await InlineKeyboards.extend_subscription_options(subscription_id)
    await callback.message.answer(
        text=LEXICON_RU['extend_sub'],
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(SubscriptionCallbackFactory.filter(F.action == 'extend_with_key'))
async def extend_with_key(callback: CallbackQuery, callback_data: SubscriptionCallbackFactory):
    subscription_id = callback_data.subscription_id
    async with DatabaseContextManager() as session_methods:
        try:
            subs = await session_methods.subscription.get_subscription(callback.from_user.id)
            if subs:
                for sub in subs:
                    if sub.subscription_id == subscription_id:
                        await callback.answer()
                        await callback.message.delete()
                        await send_invoice_handler(message=callback.message, sub=sub)
                        break
            else:
                raise

        except Exception as e:
            logger.error('Ошибка при продлении подписки', e)
            await callback.message.answer(text="Что-то пошло не так, обратитесь в техподдержку")
            await notify_group(
                message=f'Ошибка при продлении подписки:\n{callback.message.from_user.id}\n{callback.message.from_user.username}',
                is_error=True)


@router.callback_query(SubscriptionCallbackFactory.filter(F.action == 'new_order'))
async def new_order(callback: CallbackQuery, callback_data: SubscriptionCallbackFactory):
    subscription_id = callback_data.subscription_id
    await callback.message.answer("Оформлен новый заказ.")
    await callback.answer()


async def send_invoice_handler(message: Message, sub: Any):
    try:
        prices = [LabeledPrice(label="XTR", amount=sub.price)]
        await message.answer_invoice(
            title=f"VPN на {sub.name}",
            description=f"Для продления подписки, оплати {sub.price} звезд по ссылке ниже.\n",
            prices=prices,
            provider_token="",
            payload=f"{sub.service_id}:{sub.duration_days}:{sub.server_id}:old",
            currency="XTR",
            reply_markup=await InlineKeyboards.create_pay(sub.price),
        )
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        await message.answer(text="Что-то пошло не так, обратитесь в техподдержку")


async def extend_sub_successful_payment(message: Message):
    async with DatabaseContextManager() as session_methods:
        try:
            logger.info("Transaction started for adding user and service.")
            manager = OutlineManager()
            await manager.wait_for_initialization()

            in_payload = message.successful_payment.invoice_payload.split(':')
            service_id = int(in_payload[0])
            durations_days = in_payload[1]

            subs = await session_methods.subscription.get_subscription(message.from_user.id)
            if subs:
                transaction_state = await create_transaction(message, 'successful', 'successful', session_methods)
                if not transaction_state:
                    raise Exception("Ошибка сохранения транзакции")

                for sub in subs:
                    if sub.service_id == service_id:
                        await session_methods.subscription.update_sub(Subscriptions(
                            user_id=message.from_user.id,
                            service_id=service_id,
                            vpn_key_id=sub.vpn_key_id,
                            start_date=datetime.now(),
                            end_date=datetime.now() + timedelta(days=int(durations_days)),
                            updated_at=datetime.now(),
                            status=SubscriptionStatusEnum.ACTIVE,
                        ))
                        await session_methods.vpn_keys.update_limit(vpn_key_id=sub.vpn_key_id, new_limit=0)

                        await message.answer(text=LEXICON_RU['subscription_renewed'])
                        await session_methods.session.commit()
                        await notify_group(
                            message=f'Пользователь: {message.from_user.username}\n'
                                    f'ID: {message.from_user.id}\n'
                                    f'Продлил подписку на {durations_days} дней', )
        except Exception as e:
            logger.error(f"Error during transaction processing: {e}")
            await message.answer(text=f"К сожалению, покупка отменена.\nОбратитесь в техподдержку.")
            await refund_payment(message)

            await session_methods.session.rollback()

            await create_transaction(message, status='отмена', description=str(e), session_methods=session_methods)
            await session_methods.session.commit()
            await notify_group(
                message=f'Ошибка при формировании подписки при продлении:\n{message.from_user.id}\n{message.from_user.username}',
                is_error=True)


async def create_transaction(message, status, description: str, session_methods):
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


async def new_order_successful_payment(message: Message):
    await message.answer("Новый заказ успешно оформлен!")
