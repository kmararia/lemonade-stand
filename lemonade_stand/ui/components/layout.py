"""
Page layout component
"""

import reflex as rx

from lemonade_stand.ui.components.settings import settings
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
                # Settings Modal Trigger
                settings(),
                # User Profile
                rx.el.div(
                    rx.el.button(
                        rx.icon(
                            "user", size=18, class_name="text-[var(--text-muted)] mr-2"
                        ),
                        rx.el.span(
                            f"{UIState.user_account.first_name} {UIState.user_account.last_name}",
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
                    class_name=f"shrink-0 {rx.cond(is_current_page, 'fill-[var(--selected-color)]', '')}",
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
                    flex items-center px-4 py-3 mb-2 rounded-2xl transition-all duration-300 ease-out
                    {rx.cond(UIState.is_sidebar_collapsed, "justify-center", "justify-start px-2")}
                    {rx.cond(is_current_page, active_style, inactive_style)}
                """,
            ),
            href=href,
            title=text,
            class_name="w-full block mb-1 px-4",
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
                    rounded-full p-1 shadow-sm transition-colors z-50
                """,
            ),
            rx.el.nav(
                rx.el.div(
                    sidebar_item("Overview", "layout_grid", href="/"),
                    sidebar_item("Income", "signal", href="/income"),
                    sidebar_item("Savings", "piggy-bank", href="/savings"),
                    sidebar_item("Expenses", "wallet", href="/expenses"),
                    sidebar_item("Goals", "badge_check", href="/goals"),
                    class_name="space-y-1 py-6 px-2",
                ),
            ),
            class_name="relative h-full bg-[var(--app-bg-inner)]",
        ),
        class_name=f"{rx.cond(UIState.is_sidebar_collapsed, 'w-20', 'w-60')} shrink-0 transition-all duration-300 relative border-r-2 border-[var(--border-main)] transition-colors",
    )


def page_layout(*main_content) -> rx.Component:
    """The master wrapper for every page in the app."""

    return rx.el.div(
        # Inner floating APP
        rx.el.div(
            header(),
            rx.el.div(
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
