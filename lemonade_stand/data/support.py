"""Functionality to support data processing and cleaning for the application"""

import itertools
import json
from collections.abc import Generator
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import polars as pl
from countrystatecity_countries import get_cities_of_country
from countrystatecity_countries import get_cities_of_state
from countrystatecity_countries import get_state_by_code
from countrystatecity_countries import get_states_of_country

from lemonade_stand.config import AppDir
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
APP_PATHS = AppDir()


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

    def _sort_and_chunk(self, iter_list: list) -> Generator[str, None, None]:
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
            None,
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
                city_state_map[city] = get_state_by_code(
                    country_code=self.country, state_code=matches[0].state_code
                ).name.upper()

        return city_state_map


@dataclass
class TransactionCleaner:
    """Filters out transactions that are most likely invalid"""

    input_df: pl.LazyFrame
    output_df: pl.LazyFrame = field(init=False)
    state_data: StateCities = field(default_factory=StateCities)

    def __post_init__(self):
        """Initializes the data cleaning process"""

        LOGGER.debug("Adding processed fields to the dataset...")

        self.output_df = self.input_df

        self.output_df = self.flag_exclusions()
        self.output_df = self.clean_description()
        self.output_df = self.find_locations()
        self.output_df = self.find_merchant()

    def _get_field_value_list(self, data_df: pl.LazyFrame, col_name: str) -> list:
        """Gets a list of column values"""

        return (
            data_df.filter(pl.col(col_name).is_not_null())
            .select(pl.col(col_name).str.replace_all(" ~", ""))
            .unique()
            .collect()
            .to_series()
            .to_list()
        )

    def clean_description(self) -> pl.LazyFrame:
        """
        Cleans the description field of the transaction.

        Returns:
            A polars dataframe with the cleaned description

        """

        delete_regex = (
            r"(?i)"  #                                              case-insensitive flag
            r"\bX+-?X+\b"  #                                        Xs that come from redacting ID numbers
            r"|\b[a-z0-9]*([a-z]\d|\d[a-z])[a-z0-9]*\b"  #          alternating letters and numbers that are likely to be IDs or codes
            r"|\b(TEL|WEB|PPD|PMT|PAYMENT)[\s]+ID(\:|\s)[\s\S]*"  # strings that look like ID numbers
            r"|\b(CARD|CARD\s+ENDING\s+IN|AUT)\s+\d+[\s\S]*"  #     strings that look like card or authorization numbers
            r"|\bPAYMENT\s+\d+[\s\S]*"  #                           strings that look like payment confirmations
            # r"|\b\-+\b"                                     #     hyphens strictly between characters
        )

        replace_regex = (
            r"(?i)"  #                  case-insensitive flag
            r"(HTTPS)?[\s\.]?WWW\b"  #  strings that look like start of URLs
            r"|\.com\b"  #              strings that look like end URLs
            r"|\b\d+[^\w]*\d*\b"  #     strings that are mostly numbers but may have some delimiters in between
            r"|\b\d*[^\w]*\d+\b"  #     strings that are mostly numbers but may have some delimiters in between
            r"|[^\w\s']+"  #            all symbols EXCEPT letters, numbers, spaces, and apostrophes
        )

        return self.output_df.with_columns(
            clean_description=(
                pl.col("description")
                .str.replace_all(delete_regex, "")
                .str.replace_all(replace_regex, " ")
                .str.replace_all(r"\s+", " ")
                .str.strip_chars()
                .replace("", None)
            )
        ).filter(pl.col("clean_description").is_not_null())

    def find_merchant(self) -> pl.LazyFrame:
        """
        Finds the merchant of the transaction from the description field.

        Returns:
            A polars dataframe with the merchant linked to the transaction
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
                pl.col("clean_description")
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
            A polars expression for finding the location of the transaction
        """

        location_df = self.output_df.with_columns(
            # Do the initial pull on the state name
            state=(
                pl.coalesce(
                    [
                        pl.col("clean_description").str.extract(
                            self.state_data.state_name_regex, 1
                        ),
                        pl.col("clean_description")
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
                    pl.col("clean_description").str.extract(
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
        #                             pl.col("clean_description").str.extract(
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

    def flag_exclusions(self) -> pl.LazyFrame:
        """
        Flags transactions that are listed in the user exclusion configuration file or have amount values in the description field.

        Returns:
            A polars expression for filtering out the "bad" records
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
            (
                (
                    pl.col("description")
                    .str.to_lowercase()
                    .str.count_matches(rf"{exclude_pattern}")
                    > 0
                )
                | (
                    pl.col("description")
                    .str.extract(r"(\b-?\d*,?\d+\.\d{2}\b)", 1)
                    .is_not_null()
                )
            ).alias("exclude_flag")
        )
