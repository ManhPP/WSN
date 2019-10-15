import logging
import logging.config


def init_log():
    logging.config.fileConfig('/home/manhpp/Documents/Code/WSN/utils/logging.conf')
    logger = logging.getLogger(__name__)
    logger.info("Custom logging started.")
    logger.info("Complete!")
    return logger
