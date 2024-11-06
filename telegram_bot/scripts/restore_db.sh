#!/bin/bash

# Загружаем переменные окружения из файла .env
source /srv/BotVPN/.env

# Проверяем, что переменные окружения заданы
if [[ -z "$DB_USER" || -z "$DB_PASSWORD" || -z "$DB_NAME" || -z "$DB_HOST" ]]; then
    echo "Не заданы все необходимые переменные окружения (DB_USER, DB_PASSWORD, DB_NAME, DB_HOST)"
    exit 1
fi

# Проверяем, что передан путь к файлу бэкапа
if [[ -z "$1" ]]; then
    echo "Пожалуйста, укажите путь к файлу бэкапа."
    exit 1
fi

BACKUP_FILE="$1"

# Команда для восстановления базы данных
restore_command="docker exec -e PGPASSWORD=$DB_PASSWORD $DB_HOST pg_restore --clean --no-owner --no-acl -U $DB_USER -d $DB_NAME -h localhost $BACKUP_FILE"

# Выполняем команду
echo "Восстановление базы данных из бэкапа $BACKUP_FILE..."
if eval $restore_command; then
    echo "База данных успешно восстановлена."
else
    echo "Ошибка при восстановлении базы данных."
    exit 1
fi
