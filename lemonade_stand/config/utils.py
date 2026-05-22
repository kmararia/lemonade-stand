"""Holds dataclasses for the application configuration set up"""

import json
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from pathlib import Path

from lemonade_stand.config.setup import get_user_configs

from .metadata import USER_CONFIG


@dataclass
class AppDir:
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

    def get_os_home(self) -> Path:
        """Returns the home directory of the user's operating system"""
        return Path.home()

    def get_app_root_dir(self) -> Path:
        """Returns the root working directory for the application"""
        return self.get_os_home() / ".lemonade-stand"


@dataclass
class UserConfig:
    """A dataclass for the applicaton configs"""

    app_version: str = field(init=False)
    always_refresh_data: bool = field(init=False)
    always_skip_login: bool = field(init=False)
    statement_dir: Path = field(init=False)
    dev_mode: bool = field(default=False)

    def __post_init__(self):
        """Post initialization variables set up"""
        dirs = AppDir()

        # Set up the configurations
        config_dict = get_user_configs(user_config=dirs.config_dir / "user_config.json")

        # Update object fields variables
        self.app_version = config_dict["app-version"]
        self.always_refresh_data = bool(config_dict["always-refresh-data"])
        self.always_skip_login = self.dev_mode or bool(config_dict["always-skip-login"])
        self.statement_dir = Path(
            USER_CONFIG["statement-dir"]
            if self.dev_mode
            else config_dict["statement-dir"]
        )

    def __str__(self):
        """String representation of the class"""
        print_str = [f"\t{x.name}: --> {getattr(self, x.name)}" for x in fields(self)]

        return "\n".join(print_str)

    def update_attribute(self, mappings: dict) -> None:
        """Class method to update the object attributes

        Arguments:
            mappings: A dictionary of new mappings e.g. {"my_attribute": "new_value"}

        Returns:
            None

        """
        # Update the object variables
        for attr, new_val in mappings.items():
            object.__setattr__(self, attr, new_val)

        # Initialize application directory object
        dirs = AppDir()

        # Write out new mappings to json file conditionally
        if not self.dev_mode:
            config_dict = {
                x.name.replace("_", "-"): (
                    str(getattr(self, x.name))
                    if x.name == "statement_dir"
                    else getattr(self, x.name)
                )
                for x in fields(self)
                if x.name not in ["dev_mode", "category_mappings"]
            }

            # Dump user configurations into file
            with (dirs.config_dir / "user_config.json").open("w") as file:
                json.dump(config_dict, file, indent=4)
