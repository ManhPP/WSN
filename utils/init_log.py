import logging
import logging.config
import os
from pathlib import Path


def init_log():
    config_file_path = Path(__file__).parent
    path = f"{config_file_path.parent.parent}/logs"
    if not os.path.isdir(path):
        os.makedirs(path)
    logging.config.fileConfig(f"{config_file_path}/logging.conf")
    logger = logging.getLogger(__name__)
    logger.info("Logger started.")
    return logger
