"""Holds dataclasses for the application configuration set up"""

import json
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

from .metadata import BASE_CONFIG


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

        with user_config.open("w") as file:
            json.dump(config_dict, file, indent=4)

    def get_user_configs(self):
        """Sets up application configurations. Uses saved configs or user input configs"""

        user_config = AppPaths().config_dir / "user_config.json"

        # Search for the configuration file in the path
        if user_config.exists():
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
            config_dict = BASE_CONFIG

        return config_dict

    def update_attribute(self, mappings: dict) -> None:
        """Class method to update the object attributes

        Arguments:
            mappings: A dictionary of new mappings e.g. {"my_attribute": "new_value"}

        Returns:
            None

        """

        # Update the object variables
        for attr, new_val in mappings.items():
            attr = attr.replace("-", "_")

            for class_attr in fields(self):
                if attr == class_attr.name:
                    object.__setattr__(self, class_attr.name, new_val)

                elif isinstance(getattr(self, class_attr.name), SimpleNamespace):
                    class_attr_dict = getattr(self, class_attr.name).__dict__

                    if attr in class_attr_dict:
                        new_dict = {**class_attr_dict, attr: new_val}
                        object.__setattr__(
                            self, class_attr.name, SimpleNamespace(**new_dict)
                        )
                else:
                    continue
                break
            break

        self.save_config()
