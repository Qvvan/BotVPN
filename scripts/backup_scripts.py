import os
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv('../.env')

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
BACKUP_PATH = os.getenv("BACKUP_PATH")

# Telegram параметры
TOKEN = os.getenv('BOT_TOKEN')
BACKUP_GROUP_ID = os.getenv('BACKUP_GROUP_ID')


# Создаем бэкап
def create_backup():
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = f"{BACKUP_PATH}/backup_{date_str}.sql"
    command = f"pg_dump -U {DB_USER} -h {DB_HOST} -p {DB_PORT} {DB_NAME} > {backup_file}"

    # Установка переменной окружения для PostgreSQL пароля
    env = {key: str(value) for key, value in os.environ.items()}
    env['PGPASSWORD'] = str(DB_PASSWORD)

    try:
        # Выполняем команду pg_dump
        subprocess.run(command, shell=True, check=True, env=env)
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"Backup command failed: {e}")
        return None


# Отправка документа (файла) в Telegram
def send_telegram_document(file_path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(file_path, 'rb') as document:
        params = {'chat_id': BACKUP_GROUP_ID}
        files = {'document': document}

        response = requests.post(url, params=params, files=files)

    if response.status_code == 200:
        print("Backup file sent successfully")
    else:
        print(f"Failed to send backup file. Status code: {response.status_code}")


# Отправка текстового сообщения в Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        'chat_id': BACKUP_GROUP_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    response = requests.post(url, params=params)

    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")


# Основной процесс
def main():
    backup_file = create_backup()

    if backup_file:
        success_message = f"Backup created successfully at {backup_file}"
        print(success_message)
        send_telegram_document(backup_file)  # Отправляем файл
    else:
        error_message = "Error during backup creation"
        print(error_message)
        send_telegram_message(error_message)  # Если ошибка, отправляем сообщение


if __name__ == "__main__":
    main()
