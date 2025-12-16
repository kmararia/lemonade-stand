"""
Set up a logger with handlers
"""

import logging
from pathlib import Path


def set_up_logger(
    name: str, level: int = logging.INFO, log_file_path: Path | None = None
):
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

    # Set up handlers
    console_handler = logging.StreamHandler()

    # Add formatter to handlers
    console_handler.setFormatter(formatter)

    console_handler.setLevel(level)
    logger.setLevel(level)

    # Append handlers
    logger.addHandler(console_handler)

    if log_file_path:
        # Set up directory if needed
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)

        logger.addHandler(file_handler)

    # Finalize logger
    logger.propagate = False
    logger.info("Logger set up for module %s", name)

    return logger
