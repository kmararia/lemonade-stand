"""
Sets up the application configurations
"""

import json
from pathlib import Path

from InquirerPy import inquirer
from InquirerPy import validator

from lemonade_stand.config import metadata
from lemonade_stand.utils import VersionMismatchError
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
USER_CONFIG = metadata.USER_CONFIG


def check_version(config_path: Path, config_dict: dict):
    """
    Validates that the embedding data exists and is upto date
    """

    def _write_config(configs: dict):
        with config_path.open("w") as file:
            json.dump(configs, file, indent=4)

    # Confirm if we need to re-download data
    if not config_path.exists():
        _write_config(config_dict)
        return True

    else:
        # Check if recent version exists
        try:
            keys_check = config_dict.keys()
            config_dict = json.load(config_path.open("r"))

            if (
                all(x in keys_check for x in config_dict)
                and config_dict["version"] == config_dict["version"]
            ):
                return False
            else:
                raise VersionMismatchError("Non-matching metadata file version")

        except VersionMismatchError:
            _write_config(config_dict)
            return True


def request_user_configs(session_dir: Path) -> dict:
    """
    Request configuration prefills from the user
    """

    # Get user's statement folder path
    statement_dir = inquirer.filepath(  # type: ignore
        message=(
            "Enter statement folder path..."
            "\n - Click [Tab] for option suggestions"
            "\n - Click [Enter] if in the current dir as this application"
            "\n"
        ),
        validate=validator.PathValidator(
            is_dir=True, message="Please input a valid ** directory ** path"
        ),
        default=str(session_dir),
        only_directories=True,
    ).execute()

    # Confirm if export
    export_choice = inquirer.select(  # type: ignore
        message="Would you like to write out data?",
        choices=["Yes", "No", "Not Sure"],
    ).execute()

    # Final set ups
    USER_CONFIG["export-flag"] = export_choice == "Yes"
    USER_CONFIG["statement-directory"] = str(
        Path.cwd() if len(statement_dir.strip()) == 0 else Path(statement_dir)
    )

    return USER_CONFIG


def get_user_configs(user_config: Path, session_dir: Path):
    """
    Sets up application configurations. Uses saved configs or user input configs
    """

    # Search for the configuration file in the path
    if user_config.exists():
        if inquirer.confirm(  # type: ignore
            message="Would you like to use prior configurations?", default=True
        ).execute():  # type: ignore
            with user_config.open("r") as file:
                config_dict = json.load(file)

            # Add configurations if missing
            for key, val in USER_CONFIG.items():
                if key not in config_dict:
                    config_dict[key] = val
        else:
            config_dict = request_user_configs(session_dir)

    else:
        config_dict = request_user_configs(session_dir)

    # Write out to json file
    user_config.parent.mkdir(parents=True, exist_ok=True)

    with user_config.open("w") as file:
        json.dump(config_dict, file, indent=4)

    return config_dict
