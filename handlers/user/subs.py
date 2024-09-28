from datetime import datetime
from typing import Any

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import InlineKeyboards, SubscriptionCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger

router = Router()


@router.message(Command(commands='subs'))
async def get_user_subs(message: Message):
    user_id = message.from_user.id
    async with DatabaseContextManager() as session:
        subscription_data = await session.subscription.get_subscription(user_id)
        if subscription_data is None:
            await message.answer(text=LEXICON_RU['not_exists'])
            return
        for data in subscription_data:
            start_date = data.start_date
            end_date = data.end_date
            vpn_key = data.key
            server_name = data.server_name
            service_name = data.name
            status = data.status

            parseSubs = (
                f"📶 Статус: {'🟢 Активна' if status == 'активная' else '🔴 Истекла'}\n"
                f"💼 Услуга: {service_name}\n\n"
                f"📆 Дата начала: {start_date.strftime('%Y-%m-%d')}\n"
                f"📆 Дата окончания: {end_date.strftime('%Y-%m-%d')}\n\n"
                f"Страна: {server_name}\n"
                f"🔑 Ключ: {vpn_key}"
            )

            if status == 'истекла':
                keyboard = await InlineKeyboards.extend_subscription(data.subscription_id)
                await message.answer(
                    text=parseSubs + "\n\n🔄 Ваша подписка истекла. Хотите продлить?",
                    reply_markup=keyboard
                )
            else:
                await message.answer(text=parseSubs)


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
                        await send_invoice_handler(message=callback.message, sub=sub)
                        break
            else:
                raise

        except Exception as e:
            logger.error('Ошибка при продлении подписки', e)
            await callback.message.answer(text="Что-то пошло не так, обратитесь в техподдержку")




@router.callback_query(SubscriptionCallbackFactory.filter(F.action == 'new_order'))
async def new_order(callback: CallbackQuery, callback_data: SubscriptionCallbackFactory):
    subscription_id = callback_data.subscription_id
    await callback.message.answer("Оформлен новый заказ.")
    await callback.answer()


async def send_invoice_handler(message: Message, sub: Any):
    try:

        prices = [LabeledPrice(label="XTR", amount=1)]
        await message.answer_invoice(
            title=f"VPN на {sub.name}",
            description=f"Для продления подписки, оплати {sub.price} звезд по ссылке ниже.\n",
            prices=prices,
            provider_token="",
            payload=f"{sub.service_id}:{sub.duration_days}:{sub.server_id}",
            currency="XTR",
            reply_markup=await InlineKeyboards.create_pay(1),
        )
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        await message.answer(text="Что-то пошло не так, обратитесь в техподдержку")


# @router.pre_checkout_query()
# async def pre_checkout_query(query: PreCheckoutQuery):
#     await query.answer(ok=True)
#
#
# @router.message(F.successful_payment)
# async def successful_payment(message: Message):
#     await extend_sub_successful_payment(message)