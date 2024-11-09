from aiogram import Router
from aiogram.types import Message, CallbackQuery

from keyboards.kb_inline import InlineKeyboards, GuideSelectCallback
from keyboards.kb_reply.kb_inline import ReplyKeyboards
from lexicon.lexicon_ru import vpn_instructions_vless, vpn_instructions_outline

router = Router()


@router.message(lambda message: message.text == "Android 📱")
async def android_handler(message: Message):
    await message.answer(
        text="Выбери для какого протокола нужна инструкцию?",
        reply_markup=await InlineKeyboards.show_guide("Android")
    )


@router.message(lambda message: message.text == "iPhone 🍏")
async def iphone_handler(message: Message):
    await message.answer(
        text="Выбери для какого протокола нужна инструкцию?",
        reply_markup=await InlineKeyboards.show_guide("iPhone")
    )


@router.message(lambda message: message.text == "Windows 💻")
async def windows_macos_handler(message: Message):
    await message.answer(
        text="Выбери для какого протокола нужна инструкцию?",
        reply_markup=await InlineKeyboards.show_guide("Windows")
    )


@router.message(lambda message: message.text == "MacOS 💻")
async def windows_macos_handler(message: Message):
    await message.answer(
        text="Выбери для какого протокола нужна инструкцию?",
        reply_markup=await InlineKeyboards.show_guide("MacOS")
    )


@router.message(lambda message: message.text == "Телевизор 📺")
async def tv_handler(message: Message):
    await message.answer(
        text="Выбери для какого протокола нужна инструкцию?",
        reply_markup=await InlineKeyboards.show_guide("TV")
    )


@router.message(lambda message: message.text == "Как подключиться ❔")
async def connect_app(message: Message):
    await message.answer(
        text='Выбери свое устройство ниже 👇 для того, чтобы я показал тебе простую инструкцию подключения🔌',
        reply_markup=await ReplyKeyboards.get_menu_install_app()
    )


@router.callback_query(lambda c: c.data == 'back_to_device_selection')
async def back_to_device_selection(callback_query: CallbackQuery):
    await callback_query.message.answer(
        text='Выбери свое устройство ниже 👇 для того, чтобы я показал тебе простую инструкцию подключения🔌',
        reply_markup=await ReplyKeyboards.get_menu_install_app()
    )
    await callback_query.answer()


@router.callback_query(GuideSelectCallback.filter())
async def handle_guide_select(callback_query: CallbackQuery, callback_data: GuideSelectCallback):
    protocol = callback_data.name_app
    device = callback_data.name_oc
    await callback_query.answer()

    if protocol == 'vless':
        await callback_query.message.edit_text(
            text=vpn_instructions_vless[device],
            reply_markup=await InlineKeyboards.get_back_button_keyboard(callback="back_to_device_selection"),
            parse_mode='Markdown'
        )
    elif protocol == 'outline':
        await callback_query.message.edit_text(
            text=vpn_instructions_outline[device],
            reply_markup=await InlineKeyboards.get_back_button_keyboard(callback="back_to_device_selection"),
            parse_mode='Markdown'
        )
    elif protocol == 'back':
        await callback_query.message.answer(
            text='Выбери свое устройство ниже 👇 для того, чтобы я показал тебе простую инструкцию подключения🔌',
            reply_markup=await ReplyKeyboards.get_menu_install_app()
        )
    else:
        await callback_query.message.answer(
            text='Неизвестный протокол. Пожалуйста, попробуйте снова.'
        )
