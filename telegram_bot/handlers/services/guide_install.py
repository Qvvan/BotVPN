from aiogram import Router
from aiogram.types import Message, CallbackQuery

from keyboards.kb_inline import InlineKeyboards, GuideSelectCallback
from keyboards.kb_reply.kb_inline import ReplyKeyboards

router = Router()


@router.message(lambda message: message.text == "Android 📱")
async def android_handler(message: Message):
    await message.answer(
        text="Выбери для какого протокола нужна инструкцию?",
        reply_markup=await InlineKeyboards.show_guide("android")
    )


@router.message(lambda message: message.text == "iPhone 🍏")
async def iphone_handler(message: Message):
    await message.answer(
        text="Выбери для какого протокола нужна инструкцию?",
        reply_markup=await InlineKeyboards.show_guide("iphone")
    )


@router.message(lambda message: message.text == "Windows/MacOS 💻")
async def windows_macos_handler(message: Message):
    await message.answer(
        text="Выбери для какого протокола нужна инструкцию?",
        reply_markup=await InlineKeyboards.show_guide("windows_macos")
    )


@router.message(lambda message: message.text == "Телевизор 📺")
async def tv_handler(message: Message):
    await message.answer(
        text="Выбери для какого протокола нужна инструкцию?",
        reply_markup=await InlineKeyboards.show_guide("tv")
    )


@router.message(lambda message: message.text == "Как подключиться ❔")
async def connect_app(message: Message):
    await message.answer(
        text='Выбери свое устройство ниже 👇 для того, чтобы я показал тебе простую инструкцию подключения🔌',
        reply_markup=await ReplyKeyboards.get_menu_install_app()
    )


@router.callback_query(GuideSelectCallback.filter())
async def handle_guide_select(callback_query: CallbackQuery, callback_data: GuideSelectCallback):
    protocol = callback_data.name_app
    device = callback_data.name_oc

    if protocol == 'vless':
        await callback_query.message.answer(
            text=f'Вы выбрали протокол VLESS для устройства {device}. Вот инструкция по настройке...'
        )
    elif protocol == 'outline':
        await callback_query.message.answer(
            text=f'Вы выбрали протокол OUTLINE для устройства {device}. Вот инструкция по настройке...'
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

    await callback_query.answer()