import logging
import logging.config


def init_log():
    logging.config.fileConfig('D:\\Code\\WSN\\utils\\logging.conf')
    logger = logging.getLogger(__name__)
    logger.info("Custom logging started.")
    logger.info("Complete!")
    return logger
