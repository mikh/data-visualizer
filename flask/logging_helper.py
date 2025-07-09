"""Module logging_setup helps setup logging for another module."""

import os
import logging
import logging.handlers


def init_logging(
    module_name: str, verbose: bool, log_directory: str, log_filename: str
) -> logging.Logger:
    """Initializes logger for script."""
    root_logger = logging.getLogger()
    root_logger.handlers = []
    logger = logging.getLogger(module_name)
    logger.propagate = False

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    format_string = "[%(levelname)s]: %(name)s: %(asctime)s::: %(message)s"
    if verbose:
        format_string = (
            "[%(levelname)s]: %(filename)s:%(funcName)s:%(lineno)d => "
            "%(name)s: %(asctime)s::: %(message)s"
        )

    formatter = logging.Formatter(format_string)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if not os.path.isdir(log_directory):
        os.makedirs(log_directory)
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_directory, log_filename),
        mode="w",
        backupCount=5,
        delay=True,
    )
    # if os.path.isfile(os.path.join(log_directory, log_filename)):
    #     file_handler.doRollover()
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.debug("logging initialized")
    return logger
