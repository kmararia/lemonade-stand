"""Sets up the application configurations"""

import json
from pathlib import Path

from lemonade_stand.config import metadata
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils.exceptions import VersionMismatchError

LOGGER = set_up_logger(Path(__file__).stem)
USER_CONFIG = metadata.USER_CONFIG


def check_version(config_path: Path, config_dict: dict):
    """Validates that the embedding data exists and is upto date"""

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


def get_user_configs(user_config: Path):
    """Sets up application configurations. Uses saved configs or user input configs"""
    # Search for the configuration file in the path
    if user_config.exists():
        with user_config.open("r") as file:
            config_dict = json.load(file)

        # Add configurations if missing
        for key, val in USER_CONFIG.items():
            if key not in config_dict:
                config_dict[key] = val
    else:
        config_dict = USER_CONFIG

    # Write out to json file
    user_config.parent.mkdir(parents=True, exist_ok=True)

    with user_config.open("w") as file:
        json.dump(config_dict, file, indent=4)

    return config_dict
