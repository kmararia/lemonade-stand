"""Scrapping transactions from pdf file texts"""

import json
from pathlib import Path

import polars as pl

from lemonade_stand.config import AppDir
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
APP_PATHS = AppDir()


def generate_categories() -> pl.Expr:
    """Generates a polars expression from the user category mappings

    Arguments:
        None
    Returns:
        A polars expression for the category field creation

    """
    # Define the configuration file path
    config_path = APP_PATHS.category_config_path

    # Read in the category config file if it exists
    if config_path.exists():
        with config_path.open("r") as file:
            category_mappings: dict = json.load(file)
    else:
        category_mappings: dict = {}

    # Generate category field expression
    field_expr = pl.when(pl.lit(False)).then(pl.lit(None))

    for category, substring_list in category_mappings.items():
        lowercase_substring_list = [x.lower() for x in substring_list]

        field_expr = field_expr.when(
            pl.col("description")
            .str.to_lowercase()
            .str.contains_any(lowercase_substring_list)
        ).then(pl.lit(category))

    return field_expr


def generate_types() -> pl.Expr:
    """Generates a polars expression from the user type mappings

    Arguments:
        None
    Returns:
        A polars expression for the transaction-type field creation

    """
    # Define the configuration file path
    config_path = APP_PATHS.types_config_path

    # Read in the category config file if it exists
    if config_path.exists():
        with config_path.open("r") as file:
            transctn_type_mappings: dict = json.load(file)
    else:
        transctn_type_mappings: dict = {}

    # Generate category field expression
    field_expr = pl.when(pl.col("amount") < 0).then(pl.lit("income"))

    for transaction_type, category_list in transctn_type_mappings.items():
        lowercase_category_list = [x.lower() for x in category_list]

        field_expr = field_expr.when(
            pl.col("category")
            .str.to_lowercase()
            .str.contains_any(lowercase_category_list)
        ).then(pl.lit(transaction_type))

    return field_expr


def flag_exclusions() -> pl.Expr:
    """Filters out transactions listed in the user configuration file

    Arguments:
        data_df: A polars dadtaframe
    Returns:
        A polars dataframe without the listed records

    """
    # Define the configuration file path
    config_path = APP_PATHS.exclusions_config_path

    # Read in the category config file if it exists
    if config_path.exists():
        with config_path.open("r") as file:
            exclude_transactions: dict = json.load(file)
    else:
        exclude_transactions: dict = {"exclude": []}

    # Create the transactions filter flag
    LOGGER.debug("Creating an exclusion flag...")

    exclude_list = [x.lower() for x in exclude_transactions.get("exclude", [])]
    exclude_pattern = "|".join(exclude_list)

    return (
        pl.col("description")
        .str.to_lowercase()
        .str.count_matches(rf"{exclude_pattern}")
        > 0
    ) | (pl.col("description").str.extract(r"(\b-?\d*,?\d+\.\d{2}\b)", 1).is_not_null())


def clean_transactions(data_df: pl.DataFrame) -> pl.DataFrame:
    """Filters out transactions that are most likely invalid"""

    def save_popular_block(data_df: pl.DataFrame) -> pl.DataFrame:
        """ """

        LOGGER.debug("Saving only the necessary transaction blocks")

        # Check to see if there are multiple data tables
        date_jump_rows = (
            data_df.with_row_index(name="index")
            .with_columns(pl.col("date").shift(-1).alias("lead_date"))
            .filter(
                pl.col("date") > pl.col("date").shift(-1)  # .dt.total_days()
            )
        )

        indx_list = date_jump_rows["index"].to_list()

        # Grab the block with the most rows if needed
        if len(indx_list) > 0:
            keep_index = (indx_list[-1] + 1, len(data_df))
            prev_count = keep_index[1] - keep_index[0]

            for indx, row_indx in enumerate(indx_list):
                curr_count = (
                    row_indx + 1 if indx == 0 else row_indx - indx_list[indx - 1]
                )

                if curr_count > prev_count:
                    keep_index = (indx_list[indx - 1] + 1, row_indx + 1)
                    prev_count = curr_count

            return data_df.with_row_index(name="index").filter(
                pl.col("index").is_between(*keep_index)
            )
        else:
            return data_df

    LOGGER.debug("Filtering out bad transactions...")

    # Filter out transactions with dollar values in description
    clean_df = data_df.filter(
        pl.col("description").str.extract(r"(\b-?\d*,?\d+\.\d{2}\b)", 1).is_null()
    )

    # Pull the category and type field expressions
    categories_expr = generate_categories()
    transaction_type_expr = generate_types()
    exclude_flag_expr = flag_exclusions()

    LOGGER.debug("Adding missing fields...")

    # Populate empty columns
    clean_df = clean_df.with_columns(categories_expr.alias("category")).with_columns(
        transaction_type_expr.alias("type"),
        exclude_flag_expr.alias("exclude_flag"),
    )

    # # Filter out unnecessary data tables
    # clean_df = save_popular_block(data_df=clean_df)

    return clean_df
