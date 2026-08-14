"""Bring up module functions"""

from pathlib import Path

import polars as pl

from lemonade_stand.config import AppPaths
from lemonade_stand.config import UserConfig
from lemonade_stand.utils import read_delta
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils import write_delta
from lemonade_stand.utils.exceptions import DataLoadingError

from .clean import clean_transactions
from .read import Statement
from .utils import StateCities
from .utils import Transactions

LOGGER = set_up_logger(__name__)
APP_DATA_DIR = AppPaths().data_dir


def run_import_pipeline(user_config: UserConfig) -> Transactions:
    """Runs the data loading process"""

    LOGGER.info(
        "Loading statements from path: \n\t%s\n",
        str(user_config.data.statement_dir),
    )

    # Load all user transactions
    statements_list = []
    error_list = []

    LOGGER.info("Beginning data loading process...")

    for file in Path(user_config.data.statement_dir).glob("*.pdf"):
        try:
            statements_list.append(Statement(file_path=file))
        except DataLoadingError as e:
            error_list.append((file, str(e)))

    if len(error_list) > 0:
        LOGGER.warning(
            "The following files could not be loaded:\n\t%s",
            "\n\t".join([f"{file}: \n\t\t{error}" for file, error in error_list]),
        )

    # Get all transactions from the statements and clean them
    return Transactions(statements_list=statements_list)


def run_staging_pipeline(input_df: pl.LazyFrame) -> pl.LazyFrame:
    """Initializes the data cleaning process"""

    LOGGER.info("Beginning data cleaning process...")

    write_path = APP_DATA_DIR / "staging"
    clean_df = clean_transactions(input_df=input_df)

    # Write out to delta lake
    write_path = write_delta(
        write_dir=write_path,
        write_info_dict={"all_transactions": {"dataframe": clean_df}},
    )

    LOGGER.info("Written all transactions to delta lake path:\t-> %s\n", write_path)

    return read_delta(table="all_transactions", search_dir=write_path)


__all__ = [
    "run_import_pipeline",
    "run_staging_pipeline",
]
