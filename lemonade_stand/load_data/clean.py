"""
Functionality to support data processing and cleaning for the application
"""

import json
from pathlib import Path

import polars as pl

from lemonade_stand.config import AppPaths
from lemonade_stand.load_data.utils import StateCities
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
APP_PATHS = AppPaths()


def add_description(data_df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Adds a cleaned description field to the transaction dataframe.

    Returns:
        A polars LazyFrame with the cleaned description

    """

    delete_regex = (
        r"(?i)"  #                                              case-insensitive flag
        r"\bX+-?X+\b"  #                                        Xs that come from redacting ID numbers
        r"|\b[a-z0-9]*([a-z]\d|\d[a-z])[a-z0-9]*\b"  #          alternating letters and numbers that are likely to be IDs or codes
        r"|\b(TEL|WEB|PPD|PMT|PAYMENT)[\s]+ID(\:|\s)[\s\S]*"  # strings that look like ID numbers
        r"|\b(CARD|CARD\s+ENDING\s+IN|AUT)\s+\d+[\s\S]*"  #     strings that look like card or authorization numbers
        r"|\bPAYMENT\s+\d+[\s\S]*"  #                           strings that look like payment confirmations
        # r"|\b\-+\b"                                     #     hyphens strictly between characters
        r"|\b(ELECTRONIC PMT WEB|PAYMENT SENT|ACH WITHDRAWAL|PAYMENT THANK YOU - WEB|DEBIT PURCHASE)"  # strings that look like electronic payment confirmations
    )

    replace_regex = (
        r"(?i)"  #                  case-insensitive flag
        r"(HTTPS)?[\s\.]?WWW\b"  #  strings that look like start of URLs
        r"|\.com\b"  #              strings that look like end URLs
        r"|\b\d+[^\w]*\d*\b"  #     strings that are mostly numbers but may have some delimiters in between
        r"|\b\d*[^\w]*\d+\b"  #     strings that are mostly numbers but may have some delimiters in between
        r"|[^\w\s']+"  #            all symbols EXCEPT letters, numbers, spaces, and apostrophes
    )

    return data_df.with_columns(
        description=(
            pl.col("detail")
            .str.replace_all(delete_regex, "")
            .str.replace_all(replace_regex, " ")
            .str.replace_all(r"\s+", " ")
            .str.strip_chars()
            .replace("", None)
        )
    ).filter(pl.col("description").is_not_null())


def find_merchant(state_data: StateCities, data_df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Finds the merchant of the transaction from the description field.

    Returns:
        A polars LazyFrame with the merchant linked to the transaction
    """

    def _get_field_value_list(data_df: pl.LazyFrame, col_name: str) -> list:
        """Gets a list of column values"""

        return (
            data_df.filter(pl.col(col_name).is_not_null())
            .select(pl.col(col_name).str.replace_all(" ~", ""))
            .unique()
            .collect()
            .to_series()
            .to_list()
        )

    # Set up to remove unwanted information from the description field to make it easier to identify the merchant
    avail_city_list = _get_field_value_list(data_df, "city")
    third_party_list = [r"...\*", r"LEVELUP\*", r"PAYPAL\*"]
    payment_id_list = [
        r"ID:[\s\S]*",
        r"PAYMENT THANK YOU[\s\S]*",
        r"PAYMENT WEB[\s\S]*",
        r"PAYMENT SENT[\s\S]*",
        r"PAYMENT TO [\s\S]*? CARD ENDING.*",
    ]

    delete_regex = (
        r"(?i)\b("
        + "|".join(third_party_list + payment_id_list + avail_city_list)
        + r")\b"
    )

    return data_df.with_columns(
        merchant=(
            pl.col("description")
            .str.replace_all(state_data.state_code_regex, "")
            .str.replace_all(state_data.state_name_regex, "")
            .str.replace_all(delete_regex, "")
            .str.replace_all(r"\s+", " ")
            .str.strip_chars()
            .replace("", None)
        )
    )


def find_locations(state_data: StateCities, data_df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Finds the location of the transaction by looking for country, state, and city names in the description field.

    Returns:
        A polars LazyFrame with the location of the transaction
    """

    location_df = data_df.with_columns(
        # Do the initial pull on the state name
        state=(
            pl.coalesce(
                [
                    pl.col("description").str.extract(state_data.state_name_regex, 1),
                    pl.col("description")
                    .str.extract(state_data.state_code_regex, 1)
                    .replace_strict(state_data.code_to_name_map, default=None),
                ]
            )
            .str.strip_chars()
            .str.to_uppercase()
        )
    ).with_columns(
        city=(
            pl.when(pl.col("state").is_not_null())
            .then(
                # Check for a city name match based on the found state
                pl.col("description").str.extract(
                    pl.col("state").replace_strict(
                        state_data.regexmap_sname_city, default=None
                    ),
                    1,
                )
            )
            .str.strip_chars()
            .str.to_uppercase()
        )
    )

    return location_df


def flag_recurring_transactions(data_df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Flags recurring transactions based on historical patterns.

    Returns:
        A polars LazyFrame with a recurring flag column added
    """

    return (
        data_df.with_columns(
            pl.len().over(partition_by="merchant").alias("total_count"),
            (pl.col("amount").abs().mean().over(partition_by="merchant")).alias(
                "avg_amount"
            ),
            (pl.col("amount").abs().std().over(partition_by="merchant")).alias(
                "std_amount"
            ),
            (
                pl.col("date")
                .sort()
                .diff()
                .dt.total_days()
                .mean()
                .over(partition_by="merchant")
            ).alias("avg_days_between"),
        )
        .with_columns(
            recurring_flag=pl.when(
                (pl.col("total_count") >= 3)  # Must have a history
                & (
                    pl.col("avg_days_between").is_between(27, 32)
                )  # Happens roughly every month
                & (
                    (pl.col("std_amount") / pl.col("avg_amount")).fill_null(0) < 0.06
                )  # Amount varies by less than 6%
            )
            .then(True)
            .otherwise(False)
        )
        .drop(
            "total_count",
            "avg_amount",
            "std_amount",
            "avg_days_between",
        )
    )


def flag_exclusions(data_df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Flags transactions that are listed in the user exclusion configuration file.

    Returns:
        A polars LazyFrame with an exclusion flag column added
    """

    config_path = APP_PATHS.config_dir / "exclusions.json"

    # Read in the category config file if it exists
    if config_path.exists():
        LOGGER.debug("Creating an exclusion flag...")
        with config_path.open("r") as file:
            exclude_transactions: dict = json.load(file)

    else:
        exclude_transactions: dict = {"exclude": []}

    exclude_pattern = "|".join(
        [x.lower() for x in exclude_transactions.get("exclude", [])]
    )

    return data_df.with_columns(
        exclude_flag=(
            pl.col("description")
            .str.to_lowercase()
            .str.count_matches(rf"{exclude_pattern}")
            > 0
        )
    )


def clean_transactions(
    input_df: pl.LazyFrame,
    state_data: StateCities | None = None,
):
    """Initializes the data cleaning process"""

    state_data = StateCities() if state_data is None else state_data

    def adjust_amount_sign(data_df: pl.LazyFrame) -> pl.LazyFrame:
        """
        Update the amount field if the statement source has a majority of negative amounts.

        Returns:
            A polars LazyFrame with the amount field updated to have the correct sign
        """

        return data_df.with_columns(
            amount=pl.when((pl.col("amount") < 0).mean().over("source_file") >= 0.7)
            .then(pl.col("amount").abs())
            .otherwise(pl.col("amount"))
        )

    LOGGER.debug("Adding processed fields to the dataset...")

    output_df = adjust_amount_sign(data_df=input_df)
    output_df = add_description(data_df=output_df)
    output_df = find_locations(state_data=state_data, data_df=output_df)
    output_df = find_merchant(state_data=state_data, data_df=output_df)
    output_df = flag_recurring_transactions(data_df=output_df)
    output_df = flag_exclusions(data_df=output_df)

    return output_df
