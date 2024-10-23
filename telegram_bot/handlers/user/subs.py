from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import InlineKeyboards, SubscriptionCallbackFactory
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger

from utils.invoice_helper import send_invoice

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
    await callback.answer()
    async with DatabaseContextManager() as session_methods:
        try:
            subs = await session_methods.subscription.get_subscription(callback.from_user.id)
            if subs:
                for sub in subs:
                    if sub.subscription_id == subscription_id:
                        await callback.message.delete()
                        await send_invoice(
                            message=callback.message,
                            price=sub.price,
                            description=f"Для продления подписки, оплати {sub.price} звезд по ссылке ниже.",
                            service_name=sub.name,
                            service_id=sub.service_id,
                            duration_days=sub.duration_days,
                            action='old',
                            subscription_id=sub.subscription_id,
                        )
                        break
            else:
                raise

        except Exception as e:
            logger.error('Ошибка при продлении подписки', e)
            await callback.message.answer(text="Что-то пошло не так, обратитесь в техподдержку")