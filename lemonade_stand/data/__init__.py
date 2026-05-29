"""Bring up module functions"""

from pathlib import Path
from types import SimpleNamespace

from lemonade_stand.config import AppPaths
from lemonade_stand.config import UserConfig
from lemonade_stand.utils import read_delta
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils.exceptions import MissingDeltaError

from .utils import UserData

LOGGER = set_up_logger(Path(__file__).stem)


def get_data(config: UserConfig) -> UserData | SimpleNamespace:
    """A function to read data from database if exists otherwise process from start"""

    if not config.always_refresh_data:
        LOGGER.info("Reading pre-processed tables from data directory")

        try:
            read_dir = AppPaths().data_dir
            return SimpleNamespace(
                income=read_delta(table="income", search_dir=read_dir),
                savings=read_delta(table="savings", search_dir=read_dir),
                expenses=read_delta(table="expenses", search_dir=read_dir),
                unknown=read_delta(table="unknown", search_dir=read_dir),
            )
        except MissingDeltaError as e:
            LOGGER.warning(
                "An error occurred while reading pre-processed tables: %s. Processing data from start.",
                e,
            )

            return UserData(user_config=config)

    else:
        return UserData(user_config=config)


# Expose only the user data
__all__ = ["get_data"]
