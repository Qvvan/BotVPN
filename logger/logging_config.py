import logging


def setup_logging():
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - LINE %(lineno)d - %(message)s')

    # Создаем обработчик для вывода логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Настройка корневого логгера
    logging.basicConfig(level=logging.DEBUG, handlers=[console_handler])
