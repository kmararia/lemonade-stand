"""Holds dataclasses for the application configuration set up"""

import json
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

from lemonade_stand.utils import set_up_logger

from .metadata import BASE_CONFIG

LOGGER = set_up_logger(__name__)


@dataclass
class AppPaths:
    """A dataclass for the applicaton directories"""

    root_dir: Path = field(init=False)
    config_dir: Path = field(init=False)
    data_dir: Path = field(init=False)
    model_dir: Path = field(init=False)
    metadata_path: Path = field(init=False)

    def __post_init__(self):
        """Post initialization variables set up"""

        self.root_dir = self.get_app_root_dir()
        self.metadata_path = self.root_dir / "metadata.json"
        self.config_dir = self.root_dir / "configs"
        self.data_dir = self.root_dir / "shared" / "data"
        self.model_dir = self.root_dir / "shared" / "model"

    def __str__(self):
        """String representation of the class"""
        print_str = [f"{x.name}: \n\t--> {getattr(self, x.name)}" for x in fields(self)]

        return "\n".join(print_str)

    def get_os_home(self) -> Path:
        """Returns the home directory of the user's operating system"""
        return Path.home()

    def get_app_root_dir(self) -> Path:
        """Returns the root working directory for the application"""
        return self.get_os_home() / ".lemonade-stand"


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


@dataclass
class UserConfig:
    """A dataclass for the applicaton configs"""

    app_version: str = field(init=False)
    data: SimpleNamespace = field(init=False)
    model: SimpleNamespace = field(init=False)
    ui: SimpleNamespace = field(init=False)

    def __post_init__(self):
        """Post initialization variables set up"""

        def clean_dict_key(input_dict):
            return {k.replace("-", "_"): v for k, v in input_dict.items()}

        config_dict = self.get_user_configs()

        # Update object fields variables
        self.app_version = config_dict["app-version"]
        self.data = SimpleNamespace(**clean_dict_key(config_dict["data"]))
        self.model = SimpleNamespace(**clean_dict_key(config_dict["model"]))
        self.ui = SimpleNamespace(**clean_dict_key(config_dict["ui"]))

        self.save_config()

    def __str__(self):
        """String representation of the class"""
        print_str = [
            (
                f"\t{x.name}: --> {getattr(self, x.name)}"
                if not isinstance(getattr(self, x.name), SimpleNamespace)
                else f"\t{x.name}: -->\n"
                + "\n".join(
                    [f"\t\t{x}: {y}" for x, y in getattr(self, x.name).__dict__.items()]
                )
            )
            for x in fields(self)
        ]

        return "\n".join(print_str)

    def save_config(self):
        """Saves the user configuration to a json file"""

        config_dict = {
            x.name.replace("_", "-"): (
                getattr(self, x.name)
                if not isinstance(getattr(self, x.name), SimpleNamespace)
                else {
                    x.replace("_", "-"): (y if not isinstance(y, Path) else str(y))
                    for x, y in getattr(self, x.name).__dict__.items()
                }
            )
            for x in fields(self)
        }

        # Dump user configurations into json file
        user_config = AppPaths().config_dir / "user_config.json"
        user_config.parent.mkdir(parents=True, exist_ok=True)

        if user_config.exists() and config_dict == json.load(user_config.open("r")):
            pass
        else:
            with user_config.open("w") as file:
                json.dump(config_dict, file, indent=4)

            LOGGER.info("User configuration saved to: \n\t%s", user_config)

    def get_user_configs(self):
        """Sets up application configurations. Uses saved configs or user input configs"""

        user_config = AppPaths().config_dir / "user_config.json"

        # Search for the configuration file in the path
        if user_config.exists():
            LOGGER.info("Loading user configuration file from: \n\t%s", user_config)

            with user_config.open("r") as file:
                config_dict = json.load(file)

            # Add configurations if missing
            for key, val in BASE_CONFIG.items():
                if key not in config_dict:
                    config_dict[key] = val
                if isinstance(val, dict):
                    for sub_key, sub_val in val.items():
                        if sub_key not in config_dict[key]:
                            config_dict[key][sub_key] = sub_val
                        elif isinstance(sub_val, Path):
                            config_dict[key][sub_key] = Path(config_dict[key][sub_key])
                        elif isinstance(sub_val, bool):
                            config_dict[key][sub_key] = bool(config_dict[key][sub_key])
        else:
            LOGGER.info("User configuration file not found. Using base configuration.")
            config_dict = BASE_CONFIG

        return config_dict

    def update_attribute(self, mappings: dict) -> None:
        """Class method to update the object attributes

        Arguments:
            mappings: A dictionary of new mappings e.g. {"my_attribute": "new_value"}

        Returns:
            None

        """

        LOGGER.info(
            "Updating user configuration with the following mappings: \n%s", mappings
        )

        # Update the object variables
        for attr, new_val in mappings.items():
            attr = attr.replace("-", "_")

            for class_attr in fields(self):
                if attr == class_attr.name:
                    typed_val = (
                        new_val
                        if not isinstance(getattr(self, class_attr.name), Path)
                        else Path(new_val)
                    )
                    object.__setattr__(self, class_attr.name, typed_val)
                    break

                elif isinstance(getattr(self, class_attr.name), SimpleNamespace):
                    class_attr_dict = getattr(self, class_attr.name).__dict__

                    if attr in class_attr_dict:
                        typed_val = (
                            new_val
                            if not isinstance(class_attr_dict[attr], Path)
                            else Path(new_val)
                        )
                        new_dict = {**class_attr_dict, attr: typed_val}
                        object.__setattr__(
                            self, class_attr.name, SimpleNamespace(**new_dict)
                        )
                        break

        self.save_config()
