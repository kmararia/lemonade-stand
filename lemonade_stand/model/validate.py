""" """

import json
from pathlib import Path

from lemonade_stand.config import metadata
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils.exceptions import VersionMismatchError

LOGGER = set_up_logger(Path(__file__).stem)
BASE_CONFIG = metadata.BASE_CONFIG


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
