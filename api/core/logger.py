import logging
from logging.handlers import RotatingFileHandler
from api.config import settings


log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("wallet_api")

    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=20000000,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(log_format))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    return logger

logger = setup_logger()
