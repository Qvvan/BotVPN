import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(name)s - %(filename)s - line: %(lineno)d - %(message)s")

file_handler = logging.FileHandler('bot.log')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
