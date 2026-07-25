"""
Settings page for the Lemonade Stand app.
This page allows users to manage their account settings, preferences, and security options.
"""

import reflex as rx

from lemonade_stand.ui.states.ui_state import AccountState
from lemonade_stand.ui.states.ui_state import UIState


def settings_section(*children, title: str) -> rx.Component:
    """Wraps grouped settings in a clean, modern card."""

    return rx.card(
        rx.vstack(
            rx.heading(title, size="4", weight="bold"),
            rx.divider(margin_y="1"),
            rx.vstack(*children, spacing="5", width="100%", class_name="mt-4"),
            width="100%",
            class_name="px-2 mb-2",
        ),
        width="100%",
        class_name="py-4",
    )


def setting_row(title: str, description: str, control: rx.Component) -> rx.Component:
    """Standardizes the layout for every individual setting item."""
    return rx.hstack(
        rx.vstack(
            rx.el.span(title, class_name="text-m font-medium text-[var(--text-main)]"),
            rx.el.span(description, class_name="text-sm text-[var(--text-muted)]"),
            align_items="start",
            spacing="1",
        ),
        control,
        width="100%",
        class_name="flex items-center justify-between",
    )


def preferences_settings_tab() -> rx.Component:
    """Preferences settings tab content."""

    return rx.tabs.content(
        rx.vstack(
            # Paths Section
            settings_section(
                setting_row(
                    title="Statements directory path",
                    description="Folder containing source bank statements.",
                    control=rx.input(
                        value=UIState.user_config.statement_dir,
                        placeholder="Add statements directory path...",
                        on_change=lambda x: UIState.set_config_value(
                            "statement_dir", x
                        ),
                        width="400px",
                    ),
                ),
                setting_row(
                    title="Training file path",
                    description="File containing training data for categorization heuristics.",
                    control=rx.input(
                        value=UIState.user_config.training_file,
                        placeholder="Add training file path...",
                        on_change=lambda x: UIState.set_config_value(
                            "training_file", x
                        ),
                        width="400px",
                    ),
                ),
                title="Paths",
            ),
            # Application Behavior Section
            settings_section(
                setting_row(
                    title="Always skip login",
                    description="Bypass session identity confirmation checks on app launch",
                    control=rx.switch(
                        default_checked=UIState.user_config.always_skip_login,
                        on_change=lambda x: UIState.set_config_value(
                            "always_skip_login", x
                        ),
                    ),
                ),
                setting_row(
                    title="Always refresh data",
                    description="Build & recalculate transactions from scratch on app launch",
                    control=rx.switch(
                        default_checked=UIState.user_config.always_refresh_data,
                        on_change=lambda x: UIState.set_config_value(
                            "always_refresh_data", x
                        ),
                    ),
                ),
                title="Application Behavior Settings",
            ),
            # Appearance Section
            settings_section(
                setting_row(
                    title="Application Theme Selection",
                    description="Choose between dark, light, or system theme interfaces",
                    control=rx.select.root(
                        rx.select.trigger(width="150px"),
                        rx.select.content(
                            rx.select.item("Light", value="light"),
                            rx.select.item("Cream", value="cream"),
                            rx.select.item("Dark", value="dark"),
                            rx.select.item("Dark-Blue", value="dark-blue"),
                            rx.select.item("Dark-Green", value="dark-green"),
                            rx.select.item(
                                "System", value=rx.color_mode_cond("light", "dark")
                            ),
                        ),
                        default_value=UIState.user_config.theme,
                        on_change=lambda x: UIState.set_config_value("theme", x),
                    ),
                ),
                title="Appearance Settings",
            ),
            spacing="6",
            width="100%",
            padding_top="4",
        ),
        value="preferences",
        class_name="pt-4 my-6",
    )


def account_settings_tab() -> rx.Component:
    """Account settings tab content."""

    return rx.tabs.content(
        rx.vstack(
            # Profile Information Section
            settings_section(
                rx.vstack(
                    rx.vstack(
                        rx.el.span(
                            "First Name",
                            class_name="text-m font-medium text-[var(--text-main)]",
                        ),
                        rx.input(
                            value=AccountState.user_account.first_name,
                            placeholder="Enter first name...",
                            on_change=lambda x: AccountState.set_user_account_value(
                                "first_name", x
                            ),
                            width="300px",
                        ),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.el.span(
                            "Last Name",
                            class_name="text-m font-medium text-[var(--text-main)]",
                        ),
                        rx.input(
                            value=AccountState.user_account.last_name,
                            placeholder="Enter last name...",
                            on_change=lambda x: AccountState.set_user_account_value(
                                "last_name", x
                            ),
                            width="300px",
                        ),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.el.span(
                            "Email Address",
                            class_name="text-m font-medium text-[var(--text-main)]",
                        ),
                        rx.input(
                            value=AccountState.user_account.email,
                            placeholder="Enter email address...",
                            on_change=lambda x: AccountState.set_user_account_value(
                                "email", x
                            ),
                            width="300px",
                        ),
                        align_items="start",
                        spacing="1",
                    ),
                    width="100%",
                    spacing="5",
                ),
                title="Profile Information",
            ),
            # Data Management Section
            settings_section(
                setting_row(
                    title="Export Data",
                    description="Download a complete CSV archive of your transaction history and budgets.",
                    control=rx.button(
                        "Export Archive",
                        variant="outline",
                        color_scheme="gray",
                        cursor="pointer",
                    ),
                ),
                setting_row(
                    title="Delete Account",
                    description="Permanently remove your account and all associated transaction data.",
                    control=rx.button(
                        "Delete Account",
                        variant="soft",
                        color_scheme="red",
                        cursor="pointer",
                    ),
                ),
                title="Data Management",
            ),
            spacing="6",
            width="100%",
            padding_top="4",
        ),
        value="account",
        class_name="pt-4 my-6",
    )


def security_settings_tab() -> rx.Component:
    """Security settings tab content."""

    return rx.tabs.content(
        rx.vstack(
            # Authentication Section
            settings_section(
                setting_row(
                    title="Update Password",
                    description="Ensure your account is using a long, random password to stay secure.",
                    control=rx.button(
                        "Change Password",
                        variant="outline",
                        color_scheme="gray",
                        cursor="pointer",
                    ),
                ),
                setting_row(
                    title="Two-Factor Authentication",
                    description="Add an extra layer of security to your account during login.",
                    control=rx.switch(
                        default_checked=AccountState.user_account.enable_2fa,
                        on_change=lambda x: AccountState.set_user_account_value(
                            "enable_2fa", x
                        ),
                    ),
                ),
                title="Authentication",
            ),
            # Session Management Section
            settings_section(
                setting_row(
                    title="Active Session",
                    description="Log out of your account.",
                    control=rx.dialog.close(
                        rx.button(
                            "Log out",
                            variant="soft",
                            color_scheme="orange",
                            cursor="pointer",
                            on_click=AccountState.set_logged_out,
                        ),
                    ),
                ),
                title="Session Management",
            ),
            spacing="6",
            width="100%",
            padding_top="4",
        ),
        value="security",
        class_name="pt-4 my-6",
    )


def settings() -> rx.Component:
    """Settings modal window."""

    return rx.dialog.root(
        rx.dialog.trigger(
            # Swapped to rx.el.button so it can stretch dynamically
            rx.el.button(
                rx.icon("settings", size=20, class_name="shrink-0"),
                # Adding the text so it perfectly matches the tabs when extended
                rx.cond(
                    ~UIState.is_sidebar_collapsed,
                    rx.el.span(
                        "Settings",
                        class_name="whitespace-nowrap ml-3 transition-opacity duration-300",
                    ),
                    rx.fragment(),
                ),
                class_name=f"""
                    flex items-center w-full px-4 py-3 rounded-2xl transition-all duration-300 ease-out
                    hover:bg-[var(--bg-card)] text-[var(--selected-color)] hover:text-[var(--text-main)]
                    border border-transparent z-0 hover:scale-105 cursor-pointer
                    {rx.cond(UIState.is_sidebar_collapsed, "justify-center", "justify-start px-2")}
                """,
            ),
        ),
        rx.dialog.content(
            # Title and Close Button
            rx.el.div(
                rx.dialog.title(
                    "Application Settings",
                    class_name="mb-6 text-lg font-bold text-[var(--text-main)]",
                ),
                rx.dialog.close(
                    rx.el.button(
                        rx.icon("x"),
                        variant="ghost",
                        class_name="absolute top-4 right-4 text-[var(--text-muted)] hover:text-[var(--selected-color)] transition-colors",
                    ),
                ),
                class_name="flex justify-between items-center gap-4 mb-2",
            ),
            # Application Version Display
            rx.el.div(
                rx.el.label(
                    "Application version:",
                    class_name="flex items-center block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider",
                ),
                rx.input(
                    value=UIState.user_config.app_version,
                    color_scheme="gold",
                    variant="soft",
                    size="1",
                    disabled=True,
                ),
                class_name="flex justify-start gap-4 mb-6",
            ),
            # Tabs on modal
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Account", value="account", color_scheme="mint"),
                    rx.tabs.trigger(
                        "Preferences", value="preferences", color_scheme="mint"
                    ),
                    rx.tabs.trigger("Security", value="security", color_scheme="mint"),
                ),
                account_settings_tab(),
                preferences_settings_tab(),
                security_settings_tab(),
                default_value="preferences",
                class_name="w-full",
            ),
            # Apply Updates Buttons
            rx.dialog.close(
                rx.button(
                    "Apply",
                    size="2",
                    radius="large",
                    variant="outline",
                    color_scheme="green",
                    on_click=UIState.apply_settings,
                ),
                class_name="flex justify-end items-center",
            ),
            class_name="""
                flex-1 p-6 md:p-8 max-w-4xl w-full
                bg-[var(--bg-card)] backdrop-blur-2xl rounded-2xl
                border border-[var(--border-main)]
                shadow-2xl outline-none overflow-y-auto scroll-smooth
            """,
        ),
    )
