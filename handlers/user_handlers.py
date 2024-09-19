from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from database.context_manager import DatabaseContextManager
from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU
from models.models import Users

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    user = Users(
        tg_id=message.from_user.id,
        username=message.from_user.username,
    )
    async with DatabaseContextManager() as session_methods:
        await session_methods.users.add_user(user)
        await session_methods.session.commit()
        await message.answer(text=LEXICON_RU['start'])


@router.message(Command(commands='createorder'))
async def create_order(message: Message):
    await message.answer(text=LEXICON_RU['createorder'], reply_markup=await InlineKeyboards.create_order_keyboards())


@router.message(Command(commands='subs'))
async def get_user_subs(message: Message):
    user_id = message.from_user.id
    async with DatabaseContextManager() as session:
        subscription_data = await session.subscription.get_subscription(user_id)
        if subscription_data is None:
            await message.answer(text=LEXICON_RU['not_exists'])
        for data in subscription_data:
            start_date, end_date, vpn_key, service_name = data

            parseSubs = (
                f"💼 **Услуга**: {service_name}\n\n"
                f"📆 **Дата начала**: {start_date.strftime('%Y-%m-%d')}\n"
                f"📆 **Дата окончания**: {end_date.strftime('%Y-%m-%d')}\n\n"
                f"🔑 **Ключ**: {vpn_key}"
            )

            await message.answer(text=parseSubs, parse_mode=ParseMode.MARKDOWN)

@router.message(Command(commands='support'))
async def get_support(message: Message):
    await message.answer(text=LEXICON_RU['support'], reply_markup=await InlineKeyboards.get_support(), parse_mode=ParseMode.MARKDOWN)