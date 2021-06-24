import logging


def start_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.disabled = True
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
