from config_data.config import load_config
from database.init_db.init_db import InitDB


def main():
    # Загружаем конфигурацию
    config = load_config()
    db = InitDB(config)

if __name__ == "__main__":
    main()