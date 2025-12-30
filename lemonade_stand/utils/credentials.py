"""
A module user credential validation
"""

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from types import SimpleNamespace

import bcrypt
import polars as pl

from lemonade_stand.config import AppDir

from .database_io import read_from_database
from .database_io import write_to_database
from .exceptions import MissingDatabaseError
from .logging_utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
DATABASE_PATH = AppDir().database_dir / "credentials.duckdb"


@dataclass
class LoginCredentials:
    """ """

    username: bool
    password: bool
    invalid_credentials: list = field(default_factory=lambda: [], init=False)

    def __post_init__(self):
        """
        Post initialization variables set up
        """

        self.invalid_credentials = [
            x
            for x in [
                None if self.username else "username",
                None if self.password else "password",
            ]
            if x is not None
        ]


def add_user_credentials(
    username: str,
    userpassword: bytes,
    first_name: str | None = None,
    last_name: str | None = None,
    gender: str | None = None,
) -> None:
    """
    A function to store user authentication information

    Arguments:
        username: The login username
        userpassword: The user's password

    Returns:
        None
    """

    # Define schemas for the user information
    schema_user_info = {
        "account_id": pl.Int64,
        "user_name": pl.String,
        "first_name": pl.String,
        "last_name": pl.String,
        "gender": pl.String,
    }

    schema_user_keys = {
        "account_id": pl.Int64,
        "my_string_col": pl.String,
    }

    # Read in the credentials data
    try:
        credentials_data = read_from_database(database_path=DATABASE_PATH)
    except MissingDatabaseError:
        LOGGER.info(
            "Missing database '%s'. Creating empty namespace...", DATABASE_PATH.name
        )

        credentials_data = SimpleNamespace(
            user_info=pl.Schema(schema_user_info).to_frame(),
            user_keys=pl.Schema(schema_user_keys).to_frame(),
        )

    # Set up user index and hash their password
    user_index = (credentials_data.user_info).shape[0]
    hashed_password = bcrypt.hashpw(
        password=userpassword,
        salt=bcrypt.gensalt(
            rounds=8
        ),  # Setting a cost factor during salting to increase security (slows down hashing)
    )

    # Append the new credentials to the dataframes
    user_info_df = pl.concat(
        [
            credentials_data.user_info,
            pl.DataFrame(
                {
                    "account_id": [user_index],
                    "user_name": [username],
                    "first_name": [first_name],
                    "last_name": [last_name],
                    "gender": [gender],
                }
            ),
        ],
        how="vertical_relaxed",
    )

    user_keys_df = pl.concat(
        [
            credentials_data.user_keys,
            pl.DataFrame(
                {"account_id": [user_index], "user_password": [hashed_password]}
            ),
        ],
        how="vertical_relaxed",
    )

    # Write dataframes to database
    write_to_database(
        database_path=DATABASE_PATH,
        write_info_dict={
            "user_info": user_info_df,
            "user_keys": user_keys_df,
        },
    )


def validate_user_credentials(username: str, userpassword: bytes):
    """
    A function to store user authentication information

    Arguments:
        username: The login username
        userpassword: The user's password
    """

    # Read in the credentials data
    try:
        credentials_data = read_from_database(database_path=DATABASE_PATH)

        user_info_df = credentials_data.user_info.filter(
            pl.col("user_name") == username
        )

        # If username was found, move on to check password
        if user_info_df.shape[0] == 1:
            stored_hash = user_info_df.join(
                credentials_data.user_keys, on="account_id", how="full", coalesce=True
            ).item(0, "user_password")

            # Convert both passwords to bytes and run the check
            if bcrypt.checkpw(userpassword, stored_hash.encode("utf-8")):
                LOGGER.info("User credentials matched. Login successful!")
                return LoginCredentials(
                    username=True,
                    password=True,
                )

            else:
                LOGGER.info("Invalid user password")
                return LoginCredentials(
                    username=True,
                    password=False,
                )
        else:
            LOGGER.info("Username not found in database")

    except MissingDatabaseError:
        LOGGER.info(
            "Missing database '%s'. Terminating credentials validation...",
            DATABASE_PATH.name,
        )

    # (Redundacy update) Invalidate both credentials if logic gets to this point
    return LoginCredentials(
        username=False,
        password=False,
    )
