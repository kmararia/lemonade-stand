"""
Data module
"""

from dataclasses import dataclass
from dataclasses import field

import polars as pl

from lemonade_stand.config import UserConfig
from lemonade_stand.data import Statement
from lemonade_stand.data import Transactions
from lemonade_stand.data import read_pdfplumber


@dataclass(frozen=True)
class UserData:
    """
    Dataclass for the user statement data
    """

    income: pl.DataFrame = field(init=False)
    savings: pl.DataFrame = field(init=False)
    expenses: pl.DataFrame = field(init=False)

    def __post_init__(self):
        """
        Post initialization variables set up
        """

        # Set up session configurations
        run_config = UserConfig()

        # Load all user transactions
        statements = [
            Statement(file_path=file, read_func=read_pdfplumber)
            for file in (run_config.statement_dir).glob("*.pdf")
        ]

        transactions = Transactions(statements_list=statements)

        # Rename fields
        transactions.data = transactions.data.with_columns(
            pl.lit("Category").alias("transaction_category"),
            pl.lit("income").alias("transaction_type"),
        ).rename(
            {
                "transaction_date": "date",
                "transaction_category": "category",
                "transaction_amount": "amount",
                "transaction_type": "type",
                "source_file": "source",
            }
        )

        # Create summarized datasets
        income = (
            transactions.data.filter(pl.col("type") == "income")
            .group_by(["date", "category", "source"])
            .agg(pl.col("amount").sum().alias("amount"))
        )

        savings = (
            transactions.data.filter(pl.col("type") == "savings")
            .group_by(["date", "category", "source"])
            .agg(pl.col("amount").sum().alias("amount"))
        )

        expenses = (
            transactions.data.filter(pl.col("type") == "expenses")
            .group_by(["date", "category", "source"])
            .agg(pl.col("amount").sum().alias("amount"))
        )

        # Update the object variables
        object.__setattr__(self, "income", income)
        object.__setattr__(self, "savings", savings)
        object.__setattr__(self, "expenses", expenses)


USER_DATA = UserData()
