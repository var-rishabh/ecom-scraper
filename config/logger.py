import os
import logging
from datetime import datetime

def setup_logger():
    logs_folder = 'data/logs'
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    log_file = os.path.join(logs_folder, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
