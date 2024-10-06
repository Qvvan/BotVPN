import os
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv


load_dotenv('/srv/BotVPN/.env')

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
BACKUP_PATH = os.getenv("BACKUP_PATH")

TOKEN = os.getenv('BOT_TOKEN')
BACKUP_GROUP_ID = os.getenv('BACKUP_GROUP_ID')


def create_backup():
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    backup_file = f"{BACKUP_PATH}/backup_{date_str}.dump.gz"

    # Команда для выполнения резервного копирования через Docker
    command = (
        f"docker exec -e PGPASSWORD={DB_PASSWORD} "
        f"{DB_HOST} pg_dump -F c -U {DB_USER} -h localhost -d {DB_NAME} | gzip > {backup_file}"
    )

    try:
        # Выполняем команду резервного копирования
        subprocess.run(command, shell=True, check=True)
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


def main():
    backup_file = create_backup()

    if backup_file:
        success_message = f"Backup created successfully at {backup_file}"
        print(success_message)
        send_telegram_document(backup_file)
    else:
        error_message = "Error during backup creation"
        print(error_message)
        send_telegram_message(error_message)


if __name__ == "__main__":
    main()
