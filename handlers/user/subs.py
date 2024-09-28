from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import InlineKeyboards, SubscriptionCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU

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
            start_date, end_date, vpn_key, server_name, service_name, status, subscription_id = data

            parseSubs = (
                f"📶 Статус: {'🟢 Активна' if status == 'активная' else '🔴 Истекла'}\n"
                f"💼 Услуга: {service_name}\n\n"
                f"📆 Дата начала: {start_date.strftime('%Y-%m-%d')}\n"
                f"📆 Дата окончания: {end_date.strftime('%Y-%m-%d')}\n\n"
                f"Страна: {server_name}\n"
                f"🔑 Ключ: {vpn_key}"
            )

            if status == 'истекла':
                keyboard = await InlineKeyboards.extend_subscription(subscription_id)
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
    await callback.message.answer("Продление с сохранением ключа оформлено.")
    await callback.answer()

@router.callback_query(SubscriptionCallbackFactory.filter(F.action == 'new_order'))
async def new_order(callback: CallbackQuery, callback_data: SubscriptionCallbackFactory):
    subscription_id = callback_data.subscription_id
    await callback.message.answer("Оформлен новый заказ.")
    await callback.answer()
