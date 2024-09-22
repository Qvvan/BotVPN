import logging

logging.basicConfig(
    format="%(levelname)s - %(asctime)s - %(name)s - %(filename)s - line: %(lineno)d - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)
