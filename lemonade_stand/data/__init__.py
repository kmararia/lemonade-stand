"""
Bring up module functions
"""

from pathlib import Path
from types import SimpleNamespace

from lemonade_stand.config import AppDir
from lemonade_stand.config import UserConfig
from lemonade_stand.utils import read_from_database

from .utils import UserData


def get_data() -> UserData | SimpleNamespace:
    """
    A function to read data from database if exists otherwise process from start
    """

    dirs = AppDir()
    run_config = UserConfig()

    if (dirs.database_path).exists() and (not run_config.refresh_flag):
        return SimpleNamespace(
            income=read_from_database(dirs.database_path, "income"),
            savings=read_from_database(dirs.database_path, "savings"),
            expenses=read_from_database(dirs.database_path, "expenses"),
            unknown=read_from_database(dirs.database_path, "unknown"),
        )

    else:
        return UserData(config=run_config)


# Expose only the user data
__all__ = [
    "get_data",
]
