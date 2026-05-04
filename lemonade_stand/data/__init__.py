"""Bring up module functions"""

from pathlib import Path
from types import SimpleNamespace

from lemonade_stand.config import AppDir
from lemonade_stand.config import UserConfig
from lemonade_stand.utils import read_from_database
from lemonade_stand.utils import set_up_logger

from .utils import UserData

LOGGER = set_up_logger(Path(__file__).stem)
DATABASE_PATH = AppDir().database_dir / "transactions.duckdb"


def get_data(config: UserConfig) -> UserData | SimpleNamespace:
    """A function to read data from database if exists otherwise process from start"""
    if (DATABASE_PATH).exists() and (not config.always_refresh_data):
        LOGGER.info(
            "Reading pre-processed tables from database: \n\t%s", str(DATABASE_PATH)
        )

        return SimpleNamespace(
            income=read_from_database(DATABASE_PATH, "income"),
            savings=read_from_database(DATABASE_PATH, "savings"),
            expenses=read_from_database(DATABASE_PATH, "expenses"),
            unknown=read_from_database(DATABASE_PATH, "unknown"),
        )

    else:
        return UserData(config=config)


# Expose only the user data
__all__ = ["get_data", "UserData"]
