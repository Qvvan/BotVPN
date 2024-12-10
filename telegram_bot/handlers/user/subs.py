from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import InlineKeyboards, SubscriptionCallbackFactory, StatusPay
from keyboards.kb_reply.kb_inline import ReplyKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from logger.logging_config import logger

router = Router()


@router.message(Command(commands='subs'))
async def get_user_subs(message: Message, state: FSMContext):
    user_id = message.from_user.id
    async with DatabaseContextManager() as session:
        try:
            subscription_data = await session.subscription.get_subscription(user_id)
            if subscription_data is None:
                await message.answer(text=LEXICON_RU['not_exists'])
                return
            await message.answer(
                text="Все твои подписки",
                reply_markup=await ReplyKeyboards.get_menu_help()
            )
            for data in subscription_data:
                end_date = data.end_date
                key = data.key
                status = data.status
                name_app = data.name_app
                server_name = data.server_name

                parse_subs = (
                    f"<b>📶 Статус:</b> {'🟢 Активна' if status == 'активная' else '🔴 Истекла'}\n"
                    f"<b>📱 Приложение:</b> {name_app}\n"
                    f"<b>🌐 Страна:</b> {server_name}\n"
                    f"<b>📆 Дата окончания:</b> {end_date.strftime('%Y-%m-%d')}\n"
                    f"<b>🔑 Ключ:</b>\n"
                    f"<pre>{key}</pre>"
                )

                await message.answer(
                    text=parse_subs,
                    parse_mode="HTML",
                    reply_markup=await InlineKeyboards.menu_subs(data.subscription_id, name_app, data.server_ip)
                )
                await state.update_data(server_ip=data.server_ip)

        except Exception as e:
            await logger.log_error(f'Пользователь: @{message.from_user.username}\n'
                                   f'ID: {message.from_user.id}\n'
                                   f'Ошибка при получении подписок', e)


@router.callback_query(SubscriptionCallbackFactory.filter(F.action == 'extend_subscription'))
async def extend_subscription(callback: CallbackQuery, callback_data: SubscriptionCallbackFactory, state: FSMContext):
    subscription_id = callback_data.subscription_id
    await callback.answer()

    await state.update_data(subscription_id=subscription_id)
    await state.update_data(status_pay=StatusPay.OLD)

    await callback.message.answer(
        text=LEXICON_RU['createorder'],
        reply_markup=await InlineKeyboards.create_order_keyboards(StatusPay.OLD),
    )
