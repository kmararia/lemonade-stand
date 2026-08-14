"""
Page layout component
"""

import reflex as rx

from lemonade_stand.ui.components.login import login_modal
from lemonade_stand.ui.components.settings import settings
from lemonade_stand.ui.states.data_state import DataState
from lemonade_stand.ui.states.ui_state import AccountState
from lemonade_stand.ui.states.ui_state import UIState


def header() -> rx.Component:
    """"""
    return rx.el.header(
        rx.el.div(
            # Left Side: App Branding
            rx.el.div(
                rx.icon("citrus", size=28, class_name="text-orange-500 shrink-0"),
                rx.el.h1(
                    rx.el.span("Lemonade"),
                    rx.el.span("Stand", class_name="text-indigo-500"),
                    class_name="flex items-center gap-1 text-xl font-bold text-[var(--text-main)] ml-3 tracking-tight",
                ),
                class_name="flex items-center",
            ),
            # Right Side: Search, Settings, & Profile
            rx.el.div(
                rx.el.div(
                    # Search Bar
                    rx.icon("search", size=18, class_name="text-gray-400"),
                    rx.el.input(
                        placeholder="Search...",
                        class_name="bg-transparent border-none focus:ring-0 text-sm w-full placeholder:text-[var(--text-muted)] text-[var(--text-main)] outline-none",
                    ),
                    class_name="hidden md:flex items-center gap-3 bg-[var(--bg-card)] px-4 py-2.5 rounded-full w-64 shadow-sm border border-[var(--border-main)] transition-all mr-6",
                ),
                # Color Mode Toggle
                rx.el.button(
                    rx.icon(
                        rx.match(
                            UIState.user_config.theme,
                            ("light", "sun"),
                            ("dark", "moon"),
                            ("dark-blue", "waves"),
                            ("dark-green", "tree-pine"),
                            ("cream", "coffee"),
                            "sun",
                        ),
                        size=18,
                    ),
                    on_click=UIState.cycle_theme,
                    class_name="mr-6 text-[var(--accent-color)] transition-colors",
                ),
                # User Profile
                rx.el.div(
                    rx.el.button(
                        rx.icon(
                            "user", size=18, class_name="text-[var(--text-muted)] mr-2"
                        ),
                        rx.el.span(
                            f"{AccountState.user_account.first_name} {AccountState.user_account.last_name}",
                            class_name="text-sm font-medium text-[var(--text-main)]",
                        ),
                        class_name="flex items-center group cursor-pointer",
                    ),
                ),
                class_name="flex items-center",
            ),
            class_name="flex items-center justify-between h-20 px-8 w-full bg-[var(--app-bg-inner)] border-b-2 border-[var(--border-main)] transition-colors",
        ),
        class_name="w-full shrink-0 z-20 my-3",
    )


def sidebar() -> rx.Component:
    """"""

    def sidebar_item(text: str, icon_name: str, href: str = "#") -> rx.Component:
        """"""

        # Check if the button matches the current URL
        is_current_page = rx.State.router.page.raw_path == href

        active_style = (
            "bg-[var(--bg-card)] text-[var(--selected-color)] font-black "
            "border border-[var(--border-main)] "
            "shadow-[0_8px_30px_rgb(0,0,0,0.05)] hover:shadow-[0_16px_40px_rgb(0,0,0,0.12)] "
            "hover:-translate-y-1 z-10 relative"
        )
        inactive_style = (
            "hover:bg-[var(--bg-card)] text-[var(--text-main)] "
            "border border-transparent z-0 "
            "hover:scale-105 z-0"
        )

        return rx.el.a(
            rx.el.div(
                rx.icon(
                    icon_name,
                    size=20,
                    class_name="shrink-0",
                ),
                rx.cond(
                    ~UIState.is_sidebar_collapsed,
                    rx.el.span(
                        text,
                        class_name="whitespace-nowrap ml-3 transition-opacity duration-300",
                    ),
                    rx.fragment(),
                ),
                class_name=f"""
                    flex items-center px-4 py-3 mb-3 rounded-2xl transition-all duration-300 ease-out
                    {rx.cond(UIState.is_sidebar_collapsed, "justify-center", "justify-start px-2")}
                    {rx.cond(is_current_page, active_style, inactive_style)}
                """,
            ),
            href=href,
            title=text,
            class_name="w-full block px-6",
        )

    def power_item(
        text: str, icon_name: str, action: rx.event, is_destructive: bool = False
    ) -> rx.Component:
        """A sleek, fully clickable menu row for the power menu in the sidebar."""

        # Dynamically set colors
        text_color = rx.cond(
            is_destructive,
            "text-red-500 hover:text-red-600",
            "text-[var(--text-main)] hover:text-[var(--accent-color)]",
        )
        bg_hover = rx.cond(
            is_destructive, "hover:bg-red-500/10", "hover:bg-[var(--bg-subtle)]"
        )

        return rx.el.button(
            rx.icon(icon_name, size=18, class_name="shrink-0"),
            rx.el.span(text, class_name="ml-3 font-medium text-sm"),
            on_click=action,
            class_name=f"""
                flex items-center w-full px-3 py-2 rounded-md
                transition-all duration-200 cursor-pointer
                {text_color} {bg_hover}
            """,
        )

    return rx.el.aside(
        rx.el.div(
            rx.el.button(
                rx.icon(
                    rx.cond(
                        UIState.is_sidebar_collapsed, "chevron-right", "chevron-left"
                    ),
                    size=16,
                ),
                on_click=UIState.toggle_sidebar,
                class_name="""
                    absolute -right-3.5 top-6 text-[var(--text-main)] hover:text-indigo-600
                    bg-[var(--bg-subtle)] border border-[var(--border-subtle)]
                    rounded-full shadow-sm transition-colors p-1 z-50
                """,
            ),
            rx.el.nav(
                rx.el.div(
                    sidebar_item("Overview", "layout_grid", href="/"),
                    sidebar_item("Income", "signal", href="/income"),
                    sidebar_item("Savings", "piggy-bank", href="/savings"),
                    sidebar_item("Expenses", "wallet", href="/expenses"),
                    sidebar_item("Budget & Goals", "badge_check", href="/goals"),
                    class_name="space-y-1 py-6",
                ),
                rx.el.div(
                    # Settings Modal Trigger
                    rx.el.div(
                        settings(),
                        class_name="w-full block px-6 mb-3",
                    ),
                    # Power Menu
                    rx.el.div(
                        rx.popover.root(
                            rx.popover.trigger(
                                rx.el.button(
                                    rx.icon("power", size=20, class_name="shrink-0"),
                                    rx.cond(
                                        ~UIState.is_sidebar_collapsed,
                                        rx.el.span(
                                            "Power",
                                            class_name="whitespace-nowrap ml-3 transition-opacity duration-300",
                                        ),
                                        rx.fragment(),
                                    ),
                                    class_name=f"""
                                        flex items-center w-full px-4 py-3 rounded-2xl transition-all duration-300 ease-out
                                        text-[var(--selected-color)] hover:text-[var(--critical-text)] hover:bg-[var(--critical-bg)]
                                        border border-transparent z-0 hover:scale-105 cursor-pointer
                                        {rx.cond(UIState.is_sidebar_collapsed, "justify-center", "justify-start px-2")}
                                    """,
                                ),
                            ),
                            rx.popover.content(
                                rx.el.div(
                                    power_item(
                                        text="Refresh",
                                        icon_name="refresh-cw",
                                        action=DataState.reload_data,
                                    ),
                                    power_item(
                                        text="Logout",
                                        icon_name="log-out",
                                        action=AccountState.set_logged_out,
                                    ),
                                    power_item(
                                        text="Purge Data",
                                        icon_name="trash-2",
                                        action=DataState.purge_data,
                                        is_destructive=True,
                                    ),
                                    class_name="flex flex-col w-40 p-1 gap-0.5",
                                ),
                                side="right",
                                align="end",
                                custom_attrs={"data-theme": UIState.user_config.theme},
                                class_name="bg-[var(--bg-card)] border border-[var(--border-main)] rounded-xl shadow-xl overflow-hidden",
                            ),
                        ),
                        class_name="w-full block px-6",
                    ),
                    class_name="absolute bottom-6 w-full flex flex-col",
                ),
            ),
            class_name="relative h-full bg-[var(--app-bg-inner)]",
        ),
        class_name=f"{rx.cond(UIState.is_sidebar_collapsed, 'w-20', 'w-60')} shrink-0 transition-all duration-300 relative border-r-2 border-[var(--border-main)] transition-colors",
    )


def loading_modal():
    """A modal that shows a loading and progress bar during data processing."""
    return rx.cond(
        DataState.is_processing,
        rx.el.div(
            # Inner Content Wrapper
            rx.el.div(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text(
                        DataState.step_text,
                        font_weight="bold",
                        text_align="center",
                        style={"text_shadow": "0px 2px 4px rgba(0,0,0,0.5)"},
                    ),
                    rx.progress(
                        value=DataState.progress,
                        color_scheme="blue",
                        width="100%",
                        style={
                            "& .rt-ProgressIndicator": {
                                "transition": f"transform {DataState.progress_speed} cubic-bezier(0.1, 1, 0, 1) !important"
                            }
                        },
                    ),
                    align="center",
                    spacing="4",
                    width="100%",
                ),
                class_name="w-full max-w-sm mx-auto animate-in fade-in zoom-in-95 duration-300",
            ),
            class_name="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/30 backdrop-blur-sm",
        ),
        rx.fragment(),
    )


def page_layout(*main_content) -> rx.Component:
    """The master wrapper for every page in the app."""

    return rx.el.div(
        # Inner floating APP
        rx.el.div(
            header(),
            rx.el.div(
                login_modal(),
                loading_modal(),
                sidebar(),
                rx.el.main(
                    *main_content,
                    class_name="flex-1 p-6 md:p-8 overflow-y-auto scroll-smooth text-[var(--text-main)]",
                ),
                class_name="flex-1 flex overflow-hidden",
            ),
            class_name="flex flex-col w-full h-full bg-[var(--app-bg-inner)] rounded-[2.5rem] shadow-2xl overflow-hidden border border-[var(--border-subtle)] transition-colors duration-300",
        ),
        # Bind the theme state to the root element
        custom_attrs={"data-theme": UIState.user_config.theme},
        class_name="flex h-screen w-screen bg-[var(--app-bg-outer)] p-4 md:p-6 lg:p-6 transition-colors duration-300",
    )
