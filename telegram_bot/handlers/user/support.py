from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards.kb_inline import InlineKeyboards
from lexicon.lexicon_ru import LEXICON_RU

router = Router()


@router.message(Command(commands='support'))
async def get_support(message: Message):
    await message.answer(
        text=LEXICON_RU['support'],
        reply_markup=await InlineKeyboards.get_support(),
    )


@router.callback_query(lambda c: c.data == 'vpn_issue')
async def handle_vpn_issue(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['vpn_issue_response'],
        reply_markup=await InlineKeyboards.get_back_button_keyboard(),
    )


@router.callback_query(lambda c: c.data == 'low_speed')
async def handle_low_speed(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['low_speed_response'],
        reply_markup=await InlineKeyboards.get_back_button_keyboard(),
    )


@router.callback_query(lambda c: c.data == 'install_guide')
async def handle_install_guide(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON_RU['outline_info'],
        reply_markup=await InlineKeyboards.get_back_button_keyboard()
    )


@router.callback_query(lambda c: c.data == 'back_to_support_menu')
async def handle_back_to_support_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON_RU['support'],
        reply_markup=await InlineKeyboards.get_support()
    )


@router.callback_query(lambda c: c.data == 'support_callback')
async def handle_subscribe(callback_query: CallbackQuery):
    """Обработчик кнопки 'Оформить подписку' в главном меню."""
    await callback_query.message.edit_text(
        text=LEXICON_RU['support'],
        reply_markup=await InlineKeyboards.get_support()
    )