"""
Sets up the application configurations
"""

import json
from datetime import datetime
from pathlib import Path

from InquirerPy import inquirer
from InquirerPy import validator

from banana_stand import __version__
from banana_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)

BASE_CONFIG = {
    "app-version": __version__,
    "last-updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "simulation-flag": False,
    "statement-directory": Path.cwd(),
}


def request_configs(session_dir: Path) -> dict:
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

    # Confirm if simulation
    sim_choice = inquirer.select(  # type: ignore
        message="Is this a simulation run (not intended to write out data)?",
        choices=["Yes", "No", "Not Sure"],
    ).execute()

    # Final set ups
    BASE_CONFIG["simulation-flag"] = sim_choice == "Yes"
    BASE_CONFIG["statement-directory"] = str(
        Path.cwd() if len(statement_dir.strip()) == 0 else Path(statement_dir)
    )

    return BASE_CONFIG


def set_up_configs(user_config: Path, session_dir: Path):
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
        else:
            config_dict = request_configs(session_dir)

    else:
        config_dict = request_configs(session_dir)

    # Write out to json file
    user_config.parent.mkdir(parents=True, exist_ok=True)

    with user_config.open("w") as file:
        json.dump(config_dict, file, indent=4)

    return config_dict
