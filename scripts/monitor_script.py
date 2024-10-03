import os

import psutil
import requests
from dotenv import load_dotenv

load_dotenv('/srv/BotVPN/.env')

# Замените на ваши данные
BOT_TOKEN = os.getenv('BOT_TOKEN')
ERROR_GROUP_ID = os.getenv('ERROR_GROUP_ID')

# Пороговые значения
MEMORY_THRESHOLD = 80  # Процент использования оперативной памяти
DISK_THRESHOLD = 90  # Процент использования диска
CPU_THRESHOLD = 90  # Процент загрузки CPU


def send_message(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': ERROR_GROUP_ID,
        'text': message,
    }
    requests.post(url, json=payload)


def check_system():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu = psutil.cpu_percent()

    messages = []

    # Проверка памяти
    if memory.percent > MEMORY_THRESHOLD:
        messages.append(f'⚠️ Высокое использование памяти: {memory.percent}%')

    # Проверка диска
    if disk.percent > DISK_THRESHOLD:
        messages.append(f'⚠️ Высокое использование диска: {disk.percent}%')

    # Проверка загрузки CPU
    if cpu > CPU_THRESHOLD:
        messages.append(f'⚠️ Высокая загрузка CPU: {cpu}%')

    # Отправка сообщений, если есть предупреждения
    if messages:
        message = '\n'.join(messages)
        send_message(message)
    else:
        os.system('echo Все нормально!')


if __name__ == "__main__":
    check_system()
