"""Holds dataclasses for the application statement transaction set up"""

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import overload

import polars as pl

from lemonade_stand.config import AppPaths
from lemonade_stand.config import UserConfig
from lemonade_stand.data.read import Statement
from lemonade_stand.data.support import TransactionCleaner
from lemonade_stand.utils import read_delta
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils import write_delta
from lemonade_stand.utils.exceptions import DataLoadingError

LOGGER = set_up_logger(Path(__file__).stem)


@dataclass
class Transactions:
    """A dataclass for the available statements"""

    statements_list: list[Statement] = field(default_factory=list)
    data: pl.DataFrame = field(init=False)

    def __post_init__(self):
        """Post initialization variables"""
        LOGGER.info("Creating transactions data-class...\n")

        if len(self.statements_list) > 0:
            self.data = pl.concat(
                [x.transactions for x in self.statements_list], how="vertical"
            )
        else:
            LOGGER.error("No statements pdfs were found! Setting up empty dataset...")

            self.data = pl.DataFrame(data=[], schema=Statement.schema)

    def __iter__(self):
        """Iterable for the transactions dataclass"""
        for file in self.statements_list:
            yield file.transactions

    @overload
    def add(self, file_stmt: Statement): ...

    @overload
    def add(self, file_stmt: list[Statement]): ...

    def add(self, file_stmt):
        """Appends file statements to the classs statment list"""
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


@dataclass(frozen=True)
class UserData:
    """Dataclass for the user statement data"""

    user_config: UserConfig
    income: pl.DataFrame = field(init=False)
    savings: pl.DataFrame = field(init=False)
    expenses: pl.DataFrame = field(init=False)
    unknown: pl.DataFrame = field(init=False)

    def __post_init__(self):
        """Post initialization variables set up"""
        LOGGER.info(
            "Loading statements from path: \n\t%s\n",
            str(self.user_config.statement_dir),
        )

        # Load all user transactions
        statements_list = []
        error_list = []

        for file in Path(self.user_config.statement_dir).glob("*.pdf"):
            try:
                statements_list.append(Statement(file_path=file, engine="pymullm"))
            except DataLoadingError as e:
                error_list.append((file, str(e)))

        if len(error_list) > 0:
            LOGGER.warning(
                "The following files could not be loaded:\n\t%s",
                "\n\t".join([f"{file}: \n\t\t{error}" for file, error in error_list]),
            )

        # Get all transactions from the statements and clean them
        transactions = Transactions(statements_list=statements_list)
        cleaner = TransactionCleaner(
            user_config=self.user_config, input_df=transactions.data
        )

        # Break down transactions into individual table types
        tables = ["income", "savings", "expenses", "unknown"]
        table_dict = {}

        for table in tables:
            filter_condition = (
                (pl.col("payment_type") == table)
                if table != "unknown"
                else (
                    ~pl.col("payment_type").is_in([x for x in tables if x != "unknown"])
                    | pl.col("payment_type").is_null()
                )
            )
            table_dict[table] = {
                "dataframe": cleaner.output_df.filter(filter_condition)
            }

        # Write out to delta lake
        write_path = write_delta(
            write_info_dict=table_dict,
            write_dir=AppPaths().data_dir,
        )

        LOGGER.info("Written tables to delta lake path:\n\t%s", write_path)

        for table in tables:
            object.__setattr__(
                self, table, read_delta(table=table, search_dir=write_path)
            )
