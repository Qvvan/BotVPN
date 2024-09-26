from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.context_manager import DatabaseContextManager
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
            start_date, end_date, vpn_key, server_name, service_name = data

            parseSubs = (
                f"💼 Услуга: {service_name}\n\n"
                f"📆 Дата начала: {start_date.strftime('%Y-%m-%d')}\n"
                f"📆 Дата окончания: {end_date.strftime('%Y-%m-%d')}\n\n"
                f"Страна: {server_name}\n"
                f"🔑 Ключ: {vpn_key}"
            )

            await message.answer(text=parseSubs)
