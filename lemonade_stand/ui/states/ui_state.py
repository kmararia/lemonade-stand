""""""

import typing
from dataclasses import dataclass

import reflex as rx

from lemonade_stand.config import UserConfig
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(__name__)


@dataclass
class AccountConfig:
    """"""

    first_name: str
    last_name: str
    email: str
    enable_2fa: bool


@dataclass
class SettingsConfig:
    """"""

    app_version: str
    statement_dir: str
    training_file: str
    always_skip_login: bool
    always_refresh_data: bool
    theme: str


class UIState(rx.State):
    """State for UI interactions like sidebar toggling."""

    app_config: UserConfig = UserConfig()
    config_updates: dict[str, typing.Any] = {}
    is_sidebar_collapsed: bool = True

    _refresh_tick: int = 0

    @rx.var
    def user_account(self) -> AccountConfig:
        """Returns the current user configuration on the settings page."""
        return AccountConfig(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            enable_2fa=False,
        )

    @rx.var
    def user_config(self) -> SettingsConfig:
        """Returns the current user configuration on the settings page."""
        _ = self._refresh_tick + 1
        config = self.app_config

        return SettingsConfig(
            app_version=self.app_config.app_version,
            statement_dir=str(config.data.statement_dir),
            training_file=str(config.model.training_file),
            always_refresh_data=config.data.always_refresh_data,
            always_skip_login=config.ui.always_skip_login,
            theme=config.ui.theme,
        )
        LOGGER.info("check2: \n%s", self._refresh_tick)
        LOGGER.info("check22: \n%s", self.user_config)

    @rx.event
    def toggle_sidebar(self):
        """"""
        self.is_sidebar_collapsed = not self.is_sidebar_collapsed

    @rx.event
    def collapse_sidebar(self):
        """"""
        self.is_sidebar_collapsed = True

    @rx.event
    def uncollapse_sidebar(self):
        """"""
        self.is_sidebar_collapsed = False

    @rx.event
    def set_config_value(self, config_key: str, new_value: typing.Any):
        """Updates a specific field in the edit modal form."""
        self.config_updates[config_key] = new_value

    @rx.event
    def set_user_account_value(self, config_key: str, new_value: typing.Any):
        """Updates a specific field in the user account configuration."""
        setattr(self.user_account, config_key, new_value)

    @rx.event
    def apply_settings(self):
        """"""
        self.app_config.update_attribute(mappings=self.config_updates)
        self.app_config = UserConfig()
        LOGGER.info("Updated user configuration: \n%s", self.app_config)
        self.config_updates.clear()
        self._refresh_tick += 1

        LOGGER.info("check1: \n%s", self.user_config)
        LOGGER.info("check11: \n%s", self._refresh_tick)


class ActivityState(rx.State):
    """"""

    activity_filter: str = "All"

    @rx.event
    def set_activity_filter(self, value: str):
        """Change the activity filter value."""
        self.activity_filter = value
