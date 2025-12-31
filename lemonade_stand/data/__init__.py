"""
Bring up module functions
"""

from pathlib import Path
from types import SimpleNamespace

from lemonade_stand.config import AppDir
from lemonade_stand.config import UserConfig
from lemonade_stand.utils import read_from_database

from .utils import UserData

DATABASE_PATH = AppDir().database_dir / "transactions.duckdb"


def get_data(run_config: UserConfig) -> UserData | SimpleNamespace:
    """
    A function to read data from database if exists otherwise process from start
    """

    if (DATABASE_PATH).exists() and (not run_config.refresh_flag):
        return SimpleNamespace(
            income=read_from_database(DATABASE_PATH, "income"),
            savings=read_from_database(DATABASE_PATH, "savings"),
            expenses=read_from_database(DATABASE_PATH, "expenses"),
            unknown=read_from_database(DATABASE_PATH, "unknown"),
        )

    else:
        return UserData(config=run_config)


# Expose only the user data
__all__ = ["get_data", "UserData"]
