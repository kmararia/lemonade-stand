"""Holds dataclasses for the application statement transaction set up"""

import itertools
from collections.abc import Generator
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from pathlib import Path
from typing import overload

import polars as pl
from countrystatecity_countries import get_cities_of_country
from countrystatecity_countries import get_cities_of_state
from countrystatecity_countries import get_state_by_code
from countrystatecity_countries import get_states_of_country

from lemonade_stand.load_data.read import Statement
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


@dataclass
class Transactions:
    """A dataclass for the available statements"""

    statements_list: list[Statement] = field(default_factory=list)
    data: pl.LazyFrame = field(init=False)

    def __post_init__(self):
        """Post initialization variables"""
        LOGGER.info("Creating transactions data-class...\n")

        if len(self.statements_list) > 0:
            self.data = pl.concat(
                [x.transactions for x in self.statements_list], how="vertical"
            )
        else:
            LOGGER.error("No statements pdfs were found! Setting up empty dataset...")

            statement_schema = next(x for x in fields(Statement) if x.name == "schema")
            self.data = pl.LazyFrame(
                data=[],
                schema=(
                    statement_schema.default_factory()
                    if callable(statement_schema.default_factory)
                    else {}
                ),
            )

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
