import logging

def init_logging(level=logging.INFO, format='[%(levelname)s] %(filename)s - %(lineno)d - %(message)s'):
    HANDLER = logging.StreamHandler()
    FORMATTER = logging.Formatter(format)
    HANDLER.setFormatter(FORMATTER)
    LOGGER = logging.getLogger('app')
    LOGGER.addHandler(HANDLER)
    LOGGER.setLevel(level)