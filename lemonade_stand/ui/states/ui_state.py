""""""

import typing
from dataclasses import dataclass

import reflex as rx

from lemonade_stand.config import AccountConfig
from lemonade_stand.config import UserConfig
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(__name__)
_USER_CONFIG = UserConfig()
_ACCOUNT_CONFIG = AccountConfig()


@dataclass
class SettingsConfig:
    """"""

    app_version: str
    statement_dir: str
    training_file: str
    always_skip_login: bool
    always_refresh_data: bool
    theme: str


class AccountState(rx.State):
    """State for authentication interactions like login and logout."""

    config_updates: dict[str, typing.Any] = {}
    logged_in: bool = _ACCOUNT_CONFIG.always_skip_login
    is_registering: bool = False

    _refresh: int = 0

    @rx.var
    def user_account(self) -> AccountConfig:
        """Returns the user account configuration."""
        _ = self._refresh
        return AccountConfig()

    @rx.event
    def set_logged_in(self):
        """Updates the login status of the user."""
        self.logged_in = True

    @rx.event
    def set_logged_out(self):
        """Updates the login status of the user."""
        self.logged_in = False
        self.user_account.update_attribute(mappings={"always_skip_login": False})

    @rx.event
    def set_user_account_value(self, config_key: str, new_value: typing.Any):
        """Updates a specific field in the user account configuration."""
        self.config_updates[config_key] = new_value

    @rx.event
    def toggle_registering(self):
        """Swaps the modal between Login and Create Account views."""
        self.is_registering = not self.is_registering

    @rx.event
    def apply_account_settings(self):
        """Applies the account settings."""
        self.user_account.update_attribute(mappings=self.config_updates)
        self.config_updates.clear()
        self._refresh += 1


class UIState(rx.State):
    """State for UI interactions like sidebar toggling."""

    app_config: UserConfig = _USER_CONFIG
    config_updates: dict[str, typing.Any] = {}
    is_sidebar_collapsed: bool = True

    @rx.var
    def user_config(self) -> SettingsConfig:
        """Returns the current user configuration on the settings page."""
        config = self.app_config

        return SettingsConfig(
            app_version=self.app_config.app_version,
            statement_dir=str(config.data.statement_dir),
            training_file=str(config.model.training_file),
            always_refresh_data=config.data.always_refresh_data,
            always_skip_login=config.ui.always_skip_login,
            theme=config.ui.theme,
        )

    @rx.event
    def cycle_theme(self):
        """Cycles to the next theme in the list."""
        themes = ["light", "dark", "dark-blue", "dark-green", "cream"]
        try:
            current_index = themes.index(self.user_config.theme)
            next_index = (current_index + 1) % len(themes)
            self.app_config.update_attribute(mappings={"theme": themes[next_index]})
        except ValueError:
            self.app_config.update_attribute(mappings={"theme": "light"})
        finally:
            self.app_config = UserConfig()

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
    def apply_settings(self):
        """Applies the main settings."""
        self.app_config.update_attribute(mappings=self.config_updates)
        self.app_config = UserConfig()
        self.config_updates.clear()


class ActivityState(rx.State):
    """"""

    activity_filter: str = "All"

    @rx.event
    def set_activity_filter(self, value: str):
        """Change the activity filter value."""
        self.activity_filter = value
