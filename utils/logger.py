# utils/logger.py — Version 1.0.2

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "bot.log")

def setup_logger(name="bot"):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', "%Y-%m-%d %H:%M:%S")

    # File Handler
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=2)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler (optional)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Prevent duplicate logs
    logger.propagate = False

    return logger

# Global Logger
logger = setup_logger()

# Capture unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception
