"""
Set up a logger with handlers
"""

import logging

from banana_stand.app_config.dirs import AppDir

APP_DIRECTORIES = AppDir()


def set_up_logger(name: str):
    """
    A logger set up function
    """

    # Set up logger and formatter
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )

    # Set up directory if needed
    log_file_path = APP_DIRECTORIES.root_dir / "shared" / "logs" / "banana_stand.log"
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Set up handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")

    # Add formatter to handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    console_handler.setLevel(logging.WARNING)
    file_handler.setLevel(logging.INFO)
    logger.setLevel(logging.WARNING)

    # Append handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False
    logger.info("Logger set up for module %s", name)

    return logger
