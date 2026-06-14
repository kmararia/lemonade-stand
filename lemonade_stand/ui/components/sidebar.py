""""""

import reflex as rx

from lemonade_stand.ui.states.ui_state import UIState


def sidebar_item(
    text: str, icon_name: str, href: str = "#", is_active: bool = False
) -> rx.Component:
    """"""

    active_style = "bg-white dark:bg-gray-800 shadow-sm text-indigo-600 dark:text-cyan-400 font-semibold border border-gray-100 dark:border-gray-700"
    inactive_style = "hover:bg-gray-200/50 dark:hover:bg-gray-800/50 text-gray-500 dark:text-gray-400 border border-transparent"

    return rx.el.a(
        rx.el.div(
            rx.icon(icon_name, size=20, class_name="shrink-0"),
            rx.cond(
                ~UIState.is_sidebar_collapsed,
                rx.el.span(
                    text,
                    class_name="whitespace-nowrap ml-3 transition-opacity duration-300",
                ),
                rx.fragment(),
            ),
            class_name=f"flex items-center p-3 mb-2 rounded-xl transition-all duration-200 {active_style if is_active else inactive_style}",
        ),
        href=href,
        class_name="w-full block mb-1",
        title=text,
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
                    sidebar_item("Home", "layout-dashboard", href="/"),
                    sidebar_item("Income", "line_chart", href="/income"),
                    sidebar_item("Savings", "piggy-bank", href="/savings"),
                    sidebar_item("Expenses", "receipt", href="/expenses"),
                    sidebar_item("Goals", "target", href="/goals"),
                    class_name="space-y-1 py-6 px-3",
                ),
            ),
            class_name="relative h-full bg-gray-100 dark:bg-gray-950",
        ),
        class_name=f"{'w-20' if UIState.is_sidebar_collapsed else 'w-64'} shrink-0 transition-all duration-300 relative border-r-2 border-white dark:border-gray-800 transition-colors",
    )
