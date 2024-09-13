from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создаем клавиатуру для выбора услуги
service_kb = InlineKeyboardMarkup(row_width=4)

# Добавляем кнопки для выбора количества дней
service_button1 = InlineKeyboardButton(text="30 Дней", callback_data='1')
service_button2 = InlineKeyboardButton(text="90 Дней", callback_data='2')
service_button3 = InlineKeyboardButton(text="180 Дней", callback_data='3')
service_button4 = InlineKeyboardButton(text="360 Дней", callback_data='4')

# Добавляем кнопки в клавиатуру
service_kb.add(service_button1, service_button2, service_button3, service_button4)

# Клавиатура для инструкции
instruction_kb = InlineKeyboardMarkup()
instruction_button = InlineKeyboardButton(text="Инструкция", url='https://example.com/instruction')
instruction_kb.add(instruction_button)
