from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery

router = Router()  # Создаем маршрутизатор
# Коллбэк для услуг
service_callback = CallbackData("service", "days")

@router.callback_query(F.data == 'big_button_1_pressed')
async def process_button_1_press(callback: CallbackQuery):
    await callback.message.edit_text(
        text='Была нажата БОЛЬШАЯ КНОПКА 1',
        reply_markup=callback.message.reply_markup
    )

@router.callback_query(F.data == 'big_button_2_pressed')
async def process_button_2_press(callback: CallbackQuery):
    await callback.message.edit_text(
        text='Была нажата БОЛЬШАЯ КНОПКА 2',
        reply_markup=callback.message.reply_markup
    )


# Хэндлер для обработки нажатий на кнопки с выбором услуг
@router.callback_query(service_callback.filter())
async def process_service_choice(callback: CallbackQuery, callback_data: dict):
    # Извлекаем количество дней из коллбэка
    days = callback_data['days']

    # Ответ пользователю
    await callback.message.answer(f"Вы выбрали услугу на {days} дней.")

    # Дополнительно: можно отредактировать сообщение, убрать клавиатуру и т.д.
    await callback.answer()  # Чтобы закрыть окно с загрузкой (loading)