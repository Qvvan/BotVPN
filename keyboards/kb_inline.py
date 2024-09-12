from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создаем CallbackData с именем "service" и полем "days"
service_callback = CallbackData("service", "days")

# Создаем клавиатуру для выбора услуги
service_kb = InlineKeyboardMarkup(row_width=4)

# Добавляем кнопки для выбора количества дней
service_button1 = InlineKeyboardButton(text="30 Дней", callback_data=service_callback.new(days=30))
service_button2 = InlineKeyboardButton(text="90 Дней", callback_data=service_callback.new(days=90))
service_button3 = InlineKeyboardButton(text="180 Дней", callback_data=service_callback.new(days=180))
service_button4 = InlineKeyboardButton(text="360 Дней", callback_data=service_callback.new(days=360))

# Добавляем кнопки в клавиатуру
service_kb.add(service_button1, service_button2, service_button3, service_button4)

# Клавиатура для инструкции
instruction_kb = InlineKeyboardMarkup()
instruction_button = InlineKeyboardButton(text="Инструкция", url='https://example.com/instruction')
instruction_kb.add(instruction_button)
