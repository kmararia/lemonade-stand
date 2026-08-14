""" """

import reflex as rx

from lemonade_stand.ui.states.data_state import DataState
from lemonade_stand.ui.states.ui_state import AccountState
from lemonade_stand.ui.states.ui_state import UIState


def login_form() -> rx.Component:
    """The standard username and password inputs."""
    return rx.el.div(
        # Inputs
        rx.el.div(
            rx.el.label(
                "Username",
                class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
            ),
            rx.input(
                placeholder="Enter your username",
                size="3",
                radius="large",
                on_key_down=lambda key: rx.cond(
                    key == "Enter", AccountState.set_logged_in, None
                ),
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Password",
                class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
            ),
            rx.input(
                placeholder="Enter your password",
                type="password",
                size="3",
                radius="large",
                on_key_down=lambda key: rx.cond(
                    key == "Enter", AccountState.set_logged_in, None
                ),
            ),
            class_name="mb-10",
        ),
        # Action Buttons
        rx.button(
            rx.icon("fingerprint", size=18),
            rx.el.span("Log In"),
            size="3",
            radius="large",
            on_click=[
                AccountState.set_logged_in,
                AccountState.apply_account_settings,
                DataState.load_shared_data,
            ],
            class_name="w-full bg-[var(--accent-color)] text-[var(--app-bg-inner)] font-bold hover:opacity-90 transition-opacity",
        ),
        rx.el.div(
            rx.el.span(
                "Don't have an account?",
                class_name="text-[var(--text-muted)] text-sm mr-2",
            ),
            rx.el.button(
                "Create one",
                on_click=AccountState.toggle_registering,
                class_name="text-sm font-semibold text-[var(--accent-color)] hover:underline",
            ),
            class_name="mt-10 text-center",
        ),
        class_name="w-full max-w-md mx-auto mt-12 mb-4 animate-in fade-in slide-in-from-bottom-2 duration-300",
    )


def register_form() -> rx.Component:
    """The account creation inputs."""
    return rx.el.div(
        # Inputs
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "First Name",
                    class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
                ),
                rx.input(
                    placeholder=AccountState.user_account.first_name,
                    size="3",
                    radius="large",
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Last Name",
                    class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
                ),
                rx.input(
                    placeholder=AccountState.user_account.last_name,
                    size="3",
                    radius="large",
                ),
            ),
            class_name="grid grid-cols-2 gap-4 mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Email Address",
                class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
            ),
            rx.input(
                placeholder=AccountState.user_account.email,
                type="email",
                size="3",
                radius="large",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Username",
                class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
            ),
            rx.input(
                placeholder=AccountState.user_account.username, size="3", radius="large"
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Password",
                class_name="block text-sm font-medium text-[var(--text-main)] mb-1",
            ),
            rx.input(
                placeholder="Create a password",
                type="password",
                size="3",
                radius="large",
                on_key_down=lambda key: rx.cond(
                    key == "Enter", AccountState.set_logged_in, None
                ),
            ),
            class_name="mb-10",
        ),
        # Action Buttons
        rx.button(
            "Create Account",
            size="3",
            radius="large",
            on_click=[
                AccountState.set_logged_in,
                DataState.load_shared_data,
            ],
            class_name="w-full bg-[var(--accent-color)] text-[var(--app-bg-inner)] font-bold hover:opacity-90 transition-opacity",
        ),
        rx.el.div(
            rx.el.span(
                "Already have an account?",
                class_name="text-[var(--text-muted)] text-sm mr-2",
            ),
            rx.el.button(
                "Log in instead",
                on_click=AccountState.toggle_registering,
                class_name="text-sm font-semibold text-[var(--accent-color)] hover:underline",
            ),
            class_name="mt-10 text-center",
        ),
        class_name="w-full max-w-md mx-auto mt-12 mb-4 animate-in fade-in slide-in-from-bottom-2 duration-300",
    )


def welcome_view():
    """The modern welcome view shown during demo mode."""
    return rx.vstack(
        rx.icon(
            "flask_conical",
            size=40,
            class_name="""
                mt-12 mb-4 text-[var(--accent-color)] hover:text-[var(--accent-color)]
                hover:bg-[var(--bg-subtle)] transition-colors
            """,
        ),
        rx.heading(
            "Welcome to the Live Demo!",
            size="6",
            weight="bold",
            class_name="mb-4 text-[var(--text-main)]",
        ),
        rx.text(
            "Explore the app's features with simulated sample data. No account required.",
            color="gray",
            text_align="center",
            size="3",
        ),
        rx.text(
            "Found a bug? ",
            rx.link(
                "Let me know.",
                href="https://github.com/kmararia/lemonade-stand/issues",
                underline="always",
                weight="medium",
                class_name="text-indigo-500",
            ),
            size="2",
            color="gray",
            margin_top="4",
            text_align="center",
            class_name="mt-1 mb-8",
        ),
        rx.button(
            "Explore as Guest",
            size="3",
            margin_top="4",
            color_scheme="indigo",
            cursor="pointer",
            on_click=[
                AccountState.set_logged_in,
                DataState.load_shared_data,
            ],
        ),
        align_items="center",
        padding="4",
    )


def login_modal() -> rx.Component:
    """Login modal window."""

    return rx.cond(
        AccountState.logged_in,
        rx.fragment(),
        rx.el.div(
            # Modal Content Container
            rx.el.div(
                rx.el.div(
                    # Header
                    rx.el.div(
                        rx.icon(
                            "citrus", size=28, class_name="text-orange-500 shrink-0"
                        ),
                        rx.el.h1(
                            rx.el.span("Lemonade"),
                            rx.el.span("Stand", class_name="text-indigo-500"),
                            class_name="flex items-center gap-1 text-xl font-bold text-[var(--text-main)] ml-3 tracking-tight",
                        ),
                        class_name="flex items-center",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Version:",
                            class_name="p-1 block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider",
                        ),
                        rx.input(
                            value=UIState.user_config.app_version,
                            color_scheme="gold",
                            variant="soft",
                            size="1",
                            disabled=True,
                            class_name="""
                                disabled:bg-[var(--bg-subtle)]
                                disabled:text-[var(--text-muted)]
                                disabled:[-webkit-text-fill-color:var(--text-muted)]
                                disabled:opacity-100
                                disabled:cursor-not-allowed
                            """,
                        ),
                        class_name="flex justify-end items-end gap-4",
                    ),
                    class_name="flex justify-between items-center gap-4 mt-4",
                ),
                # Dynamically switch the form based on state
                rx.cond(
                    AccountState.is_demo_account,
                    welcome_view(),
                    rx.cond(
                        AccountState.is_registering,
                        register_form(),
                        login_form(),
                    ),
                ),
                # Login switch and Theme
                rx.el.div(
                    rx.cond(
                        AccountState.is_demo_account,
                        rx.fragment(),
                        rx.cond(
                            AccountState.is_registering,
                            rx.fragment(),
                            rx.hstack(
                                rx.switch(
                                    size="1",
                                    radius="small",
                                    default_checked=AccountState.user_account.always_skip_login,
                                    on_change=lambda x: (
                                        AccountState.set_user_account_value(
                                            "always_skip_login", x
                                        )
                                    ),
                                    class_name="items-end shrink-0",
                                ),
                                rx.el.label(
                                    "always skip login",
                                    class_name="block text-sm font-medium text-[var(--text-muted)]",
                                ),
                            ),
                        ),
                    ),
                    rx.icon_button(
                        rx.icon("palette", size=18),
                        variant="ghost",
                        radius="full",
                        on_click=UIState.cycle_theme,
                        class_name="""
                            text-[var(--accent-color)] hover:text-[var(--accent-color)]
                            hover:bg-[var(--bg-subtle)] transition-colors
                        """,
                    ),
                    class_name="flex justify-between mt-3",
                ),
                class_name="""
                    flex-1 p-6 md:p-8 w-full max-w-2xl
                    bg-[var(--bg-card)] rounded-2xl
                    border border-[var(--border-subtle)] shadow-lg
                    shadow-2xl outline-none overflow-y-auto scroll-smooth
                """,
            ),
            class_name="""
                fixed inset-0 z-[9999]
                flex items-center justify-center p-4
                backdrop-blur-md bg-black/40
            """,
        ),
    )
