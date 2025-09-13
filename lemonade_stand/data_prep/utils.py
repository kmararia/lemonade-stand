"""
Holds dataclasses for the application statement transaction set up
"""

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import overload

import polars as pl

from lemonade_stand.data_prep.setup import clean_transactions
from lemonade_stand.data_prep.setup import get_transactions
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


@dataclass
class Statement:
    """
    A dataclass for a statement file
    """

    file_path: Path
    read_func: Callable
    pages: list = field(init=False)
    transactions: pl.DataFrame = field(init=False)

    def __post_init__(self):
        """
        Post initialization variables
        """

        LOGGER.info("Setting up data structure for %s", Path(self.file_path).name)

        self.pages = self.read_func(Path(self.file_path))

        full_transactions = get_transactions(
            pdf_text="\n".join(self.pages)
        ).with_columns(pl.lit(self.file_path.name).alias("source_file"))
        self.transactions = clean_transactions(data_df=full_transactions)


@dataclass
class Transactions:
    """
    A dataclass for the available statements
    """

    statements_list: list[Statement] = field(default_factory=list)
    data: pl.DataFrame = field(init=False)

    def __post_init__(self):
        """
        Post initialization variables
        """

        LOGGER.info("Setting up data structure for development transactions")

        if len(self.statements_list) > 0:
            self.data = pl.concat(
                [x.transactions for x in self.statements_list], how="vertical"
            )

    def __iter__(self):
        """
        Iterable for the transactions dataclass
        """
        for file in self.statements_list:
            yield file.transactions

    @overload
    def add(self, file_stmt: Statement): ...

    @overload
    def add(self, file_stmt: list[Statement]): ...

    def add(self, file_stmt):
        """
        Appends file statements to the classs statment list
        """

        if isinstance(file_stmt, Statement):
            self.statements_list.append(file_stmt)
        elif isinstance(file_stmt, list) and all(
            isinstance(x, Statement) for x in file_stmt
        ):
            self.statements_list += file_stmt
        else:
            raise Exception("Cannot add item to DevTransactions statements list")

        # Stack the new list and replace data
        self.data = pl.concat(
            [x.transactions for x in self.statements_list], how="vertical"
        )
