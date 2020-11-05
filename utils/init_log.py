import logging
import logging.config
import os
from pathlib import Path


def init_log():
    config_file_path = Path(__file__).parent
    path = "%s/logs"%config_file_path.parent
    if not os.path.exists(path):
        os.makedirs(path)
    logging.config.fileConfig("%s/logging.conf"%config_file_path)
    logger = logging.getLogger(__name__)
    logger.info("Logger started.")
    return logger
