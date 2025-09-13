"""
Scrapping transactions from pdf file texts
"""

import re
from datetime import datetime
from decimal import Decimal as PyDecimal
from pathlib import Path

import numpy as np
import polars as pl
from dateutil.parser import parse
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


def get_transactions(pdf_text: str) -> pl.DataFrame:
    """
    Extracts the transaction lines from a string of text

    Returns:
        A list of transaction records
    """

    LOGGER.info("Getting year of the statement")

    # Set up the statement file year
    file_year = re.search(
        re.compile(r"([A-Za-z]{3,9})\s*(\d{2}),?\s*(\b\d{4}\b)", re.IGNORECASE),
        pdf_text,
    )

    file_year = (file_year.group(3)) if file_year else (datetime.now().year)

    # Define variables
    transaction_matches = []
    date_patterns = [
        r"""
            (?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|
            Apr(?:il)?|May|Jun(?:e)?|
            Jul(?:y)?|Aug(?:ust)?|Sept(?:ember)?|
            Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+
        """,
        r"\b\d{2,4}/",
    ]

    LOGGER.info("Scraping transaction lines")

    # Iterate through all the potentail patterns
    for pattern in date_patterns:
        transactions = re.finditer(
            re.compile(
                rf"({pattern}\d{{2}})\s+(.*?)\s+(-?\d*,?\d+\.\d{{2}})",
                re.IGNORECASE | re.VERBOSE,
            ),
            pdf_text,
        )

        transaction_matches.append([line.groups() for line in transactions])

    # Set up the final schema and data
    schema = pl.Schema(
        {
            "transaction_date": pl.Date(),
            "transaction_desc": pl.String(),
            "transaction_amount": pl.Decimal(None, 2),
        }
    )

    data = [
        (
            parse(row[0], default=datetime(int(file_year), 1, 1)).date(),
            row[1],
            PyDecimal(row[2].replace(",", "")),
        )
        for row in transaction_matches[
            np.argmax(
                [len(x) for x in transaction_matches]
            )  # Get list with most transactions captured
        ]
    ]

    # Return a polars dataframe
    return pl.DataFrame(
        data=data,
        schema=schema,
        orient="row",
    )


def clean_transactions(data_df: pl.DataFrame) -> pl.DataFrame:
    """
    Filters out transactions that are most likely invalid
    """

    LOGGER.info("Filtering out bad transactions")

    # Filter out transactions with dollar values in description
    clean_df = data_df.filter(
        (
            pl.col("transaction_desc").str.extract(r"(\b-?\d*,?\d+\.\d{2}\b)", 1)
        ).is_null()
    )

    def save_popular_block(data_df: pl.DataFrame) -> pl.DataFrame:
        """ """

        LOGGER.info("Saving only the necessary transaction blocks")

        # Check to see if there are multiple data tables
        date_jump_rows = (
            data_df.with_row_index(name="index")
            .with_columns(pl.col("transaction_date").shift(-1).alias("lead_date"))
            .filter(
                pl.col("transaction_date")
                > pl.col("transaction_date").shift(-1)  # .dt.total_days()
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

    # # Filter out unnecessary data tables
    # save_popular_block(data_df=data_df)

    # Return clean dataframe
    return clean_df
