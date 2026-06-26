""""""

import reflex as rx

from lemonade_stand.ui.states.ui_state import UIState


def sidebar_item(text: str, icon_name: str, href: str = "#") -> rx.Component:
    """"""

    # Check if the button matches the current URL
    is_current_page = rx.State.router.page.raw_path == href

    active_style = (
        "bg-white dark:bg-gray-800 text-green-700 dark:text-cyan-400 font-black "
        "border border-white/50 dark:border-gray-700/50 "
        "shadow-[0_8px_30px_rgb(0,0,0,0.05)] hover:shadow-[0_16px_40px_rgb(0,0,0,0.12)] "
        "hover:-translate-y-1 z-10 relative"
    )
    inactive_style = (
        "hover:bg-gray-200/50 dark:hover:bg-gray-800/50 text-gray-600 dark:text-gray-400 "
        "border border-transparent z-0 "
        "hover:scale-105 z-0"
    )

    return rx.el.a(
        rx.el.div(
            rx.icon(
                icon_name,
                size=20,
                class_name=f"shrink-0 {rx.cond(is_current_page, 'fill-green-700 dark:fill-cyan-400', '')}",
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


def sidebar() -> rx.Component:
    """"""

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
                class_name="absolute -right-3.5 top-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full p-1 shadow-sm text-gray-500 hover:text-indigo-600 transition-colors z-50",
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
            class_name="relative h-full bg-gray-100 dark:bg-gray-950",
        ),
        class_name=f"{rx.cond(UIState.is_sidebar_collapsed, 'w-20', 'w-60')} shrink-0 transition-all duration-300 relative border-r-2 border-white dark:border-gray-800 transition-colors",
    )
