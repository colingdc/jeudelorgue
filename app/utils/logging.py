import logging
from logging.handlers import RotatingFileHandler


def build_error_handler():
    error_handler = RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=1)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    error_handler.setFormatter(formatter)
    return error_handler
