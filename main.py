from config_data.config import load_config
from database.init_db.init_db import InitDB

from logger.logging_config import setup_logging


def main():
    setup_logging()

    config = load_config()
    db = InitDB(config)


if __name__ == "__main__":
    main()
