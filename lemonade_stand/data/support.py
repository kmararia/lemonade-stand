"""Functionality to support data processing and cleaning for the application"""

import itertools
import json
import typing
from collections.abc import Generator
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import polars as pl
from countrystatecity_countries import get_cities_of_country
from countrystatecity_countries import get_cities_of_state
from countrystatecity_countries import get_state_by_code
from countrystatecity_countries import get_states_of_country

from lemonade_stand.config import AppPaths
from lemonade_stand.config import UserConfig
from lemonade_stand.model import predict_buckets
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
APP_PATHS = AppPaths()


@dataclass
class StateCities:
    """Data class to hold state and city information for the US"""

    country: str = "US"
    state_name_regex: str = field(init=False)
    state_code_regex: str = field(init=False)
    regexmap_sname_city: dict = field(init=False)
    regex_cities_generator: Generator[str, None, None] = field(init=False)

    def __post_init__(self):
        """Initializes the state and city data"""

        LOGGER.debug("Loading state and city data...")

        us_states = get_states_of_country(self.country)

        state_city_map = {
            x.name.upper(): [
                y.name.upper() for y in get_cities_of_state(self.country, x.state_code)
            ]
            for x in us_states
            if len(get_cities_of_state(self.country, x.state_code)) > 0
        }

        self.code_to_name_map = {self.get_state_code(x): x for x in state_city_map}

        self.regexmap_sname_city = {
            x: self.build_polars_regex(y) for x, y in state_city_map.items()
        }

        self.regex_cities_generator = self._sort_and_chunk(
            itertools.chain.from_iterable(state_city_map.values())
        )

        self.state_name_regex = self.build_polars_regex(
            list(self.regexmap_sname_city.keys())
        )
        self.state_code_regex = self.build_polars_regex(
            list(self.code_to_name_map.keys())
        )

    def _sort_and_chunk(
        self, iter_list: list | itertools.chain[str]
    ) -> Generator[str, None, None]:
        """Sorts a list by length and returns regex chunks"""

        sorted_list = sorted(iter_list, key=len, reverse=True)

        skip_size = len(sorted_list) // len(self.regexmap_sname_city)

        for i in range(0, len(sorted_list), skip_size):
            yield self.build_polars_regex(sorted_list[i : i + skip_size])

    def build_polars_regex(self, iter_list: list) -> str:
        """Builds regex mapping for a polars extract search"""

        return rf"(?i)\b({'|'.join(iter_list)})\b"

    def get_state_code(self, state_name: str) -> str:
        """Gets the state code for a given state name"""

        states = get_states_of_country(self.country)

        return next(
            (
                state.state_code
                for state in states
                if state.name.upper() == state_name.upper()
            ),
            "",
        )

    def get_city_state_mapping(self, cities_list: list) -> dict:
        """Creates a dictionary mapping all the city and it's state for city names in only one state"""

        city_state_map = {}

        for city in cities_list:
            matches = [
                x
                for x in get_cities_of_country(country_code=self.country)
                if x.name.upper() == city
            ]

            if len(matches) == 1:
                state_name = get_state_by_code(
                    country_code=self.country, state_code=matches[0].state_code
                )
                city_state_map[city] = (
                    state_name.name.upper() if state_name is not None else None
                )

        return city_state_map


@dataclass
class TransactionCleaner:
    """Filters out transactions that are most likely invalid"""

    user_config: UserConfig
    input_df: pl.LazyFrame
    output_df: pl.LazyFrame = field(init=False)
    state_data: StateCities = field(default_factory=StateCities)

    def __post_init__(self):
        """Initializes the data cleaning process"""

        LOGGER.debug("Adding processed fields to the dataset...")

        self.output_df = TransactionCleaner.add_description(self.input_df)
        self.output_df = self.adjust_amount_sign()
        self.output_df = self.find_category_type()
        self.output_df = self.find_locations()
        self.output_df = self.find_merchant()
        self.output_df = self.flag_recurring_transactions()
        self.output_df = self.flag_exclusions()

    def _get_field_value_list(self, data_df: pl.LazyFrame, col_name: str) -> list:
        """Gets a list of column values"""

        return (
            typing.cast(
                pl.DataFrame,
                (
                    data_df.filter(pl.col(col_name).is_not_null())
                    .select(pl.col(col_name).str.replace_all(" ~", ""))
                    .unique()
                    .collect()
                ),
            )
            .to_series()
            .to_list()
        )

    @staticmethod
    def add_description(input_df: pl.LazyFrame) -> pl.LazyFrame:
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

        return input_df.with_columns(
            description=(
                pl.col("detail")
                .str.replace_all(delete_regex, "")
                .str.replace_all(replace_regex, " ")
                .str.replace_all(r"\s+", " ")
                .str.strip_chars()
                .replace("", None)
            )
        ).filter(pl.col("description").is_not_null())

    def adjust_amount_sign(self) -> pl.LazyFrame:
        """
        Update the amount field if the statement source has a majority of negative amounts.

        Returns:
            A polars LazyFrame with the amount field updated to have the correct sign
        """

        return self.output_df.with_columns(
            amount=pl.when((pl.col("amount") < 0).mean().over("source_file") >= 0.7)
            .then(pl.col("amount").abs())
            .otherwise(pl.col("amount"))
        )

    def find_merchant(self) -> pl.LazyFrame:
        """
        Finds the merchant of the transaction from the description field.

        Returns:
            A polars LazyFrame with the merchant linked to the transaction
        """

        # Set up to remove unwanted information from the description field to make it easier to identify the merchant
        avail_city_list = self._get_field_value_list(self.output_df, "city")
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

        return self.output_df.with_columns(
            merchant=(
                pl.col("description")
                .str.replace_all(self.state_data.state_code_regex, "")
                .str.replace_all(self.state_data.state_name_regex, "")
                .str.replace_all(delete_regex, "")
                .str.replace_all(r"\s+", " ")
                .str.strip_chars()
                .replace("", None)
            )
        )

    def find_locations(self) -> pl.LazyFrame:
        """
        Finds the location of the transaction by looking for country, state, and city names in the description field.

        Returns:
            A polars LazyFrame with the location of the transaction
        """

        location_df = self.output_df.with_columns(
            # Do the initial pull on the state name
            state=(
                pl.coalesce(
                    [
                        pl.col("description").str.extract(
                            self.state_data.state_name_regex, 1
                        ),
                        pl.col("description")
                        .str.extract(self.state_data.state_code_regex, 1)
                        .replace_strict(self.state_data.code_to_name_map, default=None),
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
                            self.state_data.regexmap_sname_city, default=None
                        ),
                        1,
                    )
                )
                .str.strip_chars()
                .str.to_uppercase()
            )
        )

        return location_df

        # update_cond_expr = (pl.col("state").is_null()) & (pl.col("city").is_not_null())
        # no_state_cities = self._get_field_value_list(
        #     location_df.filter(update_cond_expr), "city"
        # )

        # return location_df.with_columns(
        #     city=(
        #         pl.when(pl.col("city").is_null())
        #         .then(
        #             # If no state is found, do a random city name match beginning with the longest city names
        #             pl.concat_str(
        #                 [
        #                     pl.coalesce(
        #                         [
        #                             pl.col("description").str.extract(
        #                                 cities_regex, 1
        #                             )
        #                             for cities_regex in self.state_data.regex_cities_generator
        #                         ]
        #                     ),
        #                     pl.lit(" ~"),
        #                 ],
        #             )
        #             .str.strip_chars()
        #             .str.to_uppercase()
        #         )
        #         .otherwise(pl.col("city"))
        #     ),
        #     state=(
        #         pl.when(update_cond_expr)
        #         .then(
        #             pl.concat_str(
        #                 [
        #                     pl.col("city")
        #                     .str.replace_all(" ~", "")
        #                     .replace_strict(
        #                         self.state_data.get_city_state_mapping(
        #                             cities_list=no_state_cities
        #                         ),
        #                         default=None,
        #                     ),
        #                     pl.lit(" ~"),
        #                 ]
        #             )
        #         )
        #         .otherwise(pl.col("state"))
        #     ),
        # )

    def find_category_type(self):
        """
        Finds the category and type of the transaction by using the description field.

        Returns:
            A polars LazyFrame with the category and type of the transaction
        """

        # Assign predicted buckets (Category and Type) to the transactions
        model_data = predict_buckets(
            config=self.user_config,
            input_data=self.output_df,
            func_field_cleaner=TransactionCleaner.add_description,
        )

        return model_data.inference_data.with_columns(
            payment_type=pl.col("category").replace_strict(
                {
                    x: str(y[0]).lower()
                    for x, y in (
                        typing.cast(
                            pl.DataFrame,
                            typing.cast(pl.LazyFrame, model_data.train_data)
                            .select("category", "payment_type")
                            .collect(),
                        )
                        .rows_by_key(
                            key="category",
                            unique=True,
                        )
                        .items()
                    )
                    if x is not None and y[0] is not None
                },
                default=None,
            )
        )

    def flag_recurring_transactions(self) -> pl.LazyFrame:
        """
        Flags recurring transactions based on historical patterns.

        Returns:
            A polars LazyFrame with a recurring flag column added
        """

        return (
            self.output_df.with_columns(
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
                        (pl.col("std_amount") / pl.col("avg_amount")).fill_null(0)
                        < 0.06
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

    def flag_exclusions(self) -> pl.LazyFrame:
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

        return self.output_df.with_columns(
            exclude_flag=(
                pl.col("description")
                .str.to_lowercase()
                .str.count_matches(rf"{exclude_pattern}")
                > 0
            )
        )
