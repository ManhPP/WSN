import logging
import logging.config
from pathlib import Path


def init_log():
    config_file_path = Path(__file__).parent

    logging.config.fileConfig(f"{config_file_path}/logging.conf")
    logger = logging.getLogger(__name__)
    logger.info("Custom logging started.")
    logger.info("Complete!")
    return logger
