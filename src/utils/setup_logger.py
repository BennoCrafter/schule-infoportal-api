import logging


def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # file_handler = logging.FileHandler("schule-infoportal-api.log")
    # file_handler.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.propagate = False

    return logger
