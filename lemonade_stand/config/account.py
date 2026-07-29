"""Holds dataclasses for the user account configuration set up"""

import json
from dataclasses import dataclass
from dataclasses import fields

from lemonade_stand.utils import set_up_logger

from .paths import AppPaths

LOGGER = set_up_logger(__name__)


@dataclass
class AccountConfig:
    """A dataclass for the account configurations"""

    username: str = "jane.doe"
    first_name: str = "Jane"
    last_name: str = "Doe"
    email: str = "jane.doe@example.com"
    enable_2fa: bool = False
    always_skip_login: bool = False

    def __post_init__(self):
        """Post initialization variables set up"""
        self.apply_account_configs()

    def save_config(self):
        """Saves the user configuration to a json file"""

        config_dict = {
            x.name.replace("_", "-"): getattr(self, x.name) for x in fields(self)
        }

        # Dump user configurations into json file
        account_config = AppPaths().config_dir / "account_config.json"
        account_config.parent.mkdir(parents=True, exist_ok=True)

        if account_config.exists() and config_dict == json.load(
            account_config.open("r")
        ):
            pass
        else:
            with account_config.open("w") as file:
                json.dump(config_dict, file, indent=4)

            LOGGER.info("Account configuration saved to: \n\t%s", account_config)

    def apply_account_configs(self) -> None:
        """Sets up account configurations. Utilizes the saved configs or user input configs"""

        user_config = AppPaths().config_dir / "account_config.json"

        # Search for the configuration file in the path
        if user_config.exists():
            LOGGER.info("Loading account configuration file from: \n\t%s", user_config)

            with user_config.open("r") as file:
                config_dict = json.load(file)
                self.update_attribute(mappings=config_dict)
        else:
            LOGGER.info(
                "Account configuration file not found. Using base configurations."
            )

        self.save_config()

    def update_attribute(self, mappings: dict) -> None:
        """Class method to update the object attributes

        Args:
            mappings: A dictionary of new mappings e.g. {"my_attribute": "new_value"}
        Returns:
            None
        """

        # Check for valid mappings and update the object attributes
        new_mappings = {
            k.replace("-", "_"): v
            for k, v in mappings.items()
            if hasattr(self, k.replace("-", "_"))
            and getattr(self, k.replace("-", "_")) != v
        }

        if len(new_mappings) > 0:
            for attr, new_val in new_mappings.items():
                setattr(self, attr, new_val)
            self.save_config()
