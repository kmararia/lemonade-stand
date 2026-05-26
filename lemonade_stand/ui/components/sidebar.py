""""""

import reflex as rx

from lemonade_stand.ui.states.ui_state import UIState


def sidebar_item(text: str, icon_name: str, href: str = "#") -> rx.Component:
    """"""

    return rx.el.a(
        rx.el.div(
            rx.icon(icon_name, size=20, class_name="shrink-0"),
            rx.cond(
                ~UIState.is_sidebar_collapsed,
                rx.el.span(
                    text, class_name="whitespace-nowrap transition-opacity duration-300"
                ),
                rx.el.span(class_name="hidden"),
            ),
            class_name=rx.cond(
                UIState.is_sidebar_collapsed,
                "flex items-center justify-center p-3 rounded-xl hover:bg-indigo-50 dark:hover:bg-cyan-900/30 hover:text-indigo-600 dark:hover:text-cyan-400 text-gray-500 dark:text-gray-400 transition-all duration-200 hover:scale-105",
                "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-indigo-50 dark:hover:bg-cyan-900/30 hover:text-indigo-600 dark:hover:text-cyan-400 text-gray-500 dark:text-gray-400 transition-all duration-200 group",
            ),
        ),
        href=href,
        class_name="w-full block mb-1",
        title=text,
    )


def sidebar() -> rx.Component:
    """"""

    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "citrus",
                        size=28,
                        class_name="text-white shrink-0 relative z-10",
                    ),
                    class_name="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-200 dark:shadow-none",
                ),
                rx.cond(
                    ~UIState.is_sidebar_collapsed,
                    rx.el.h1(
                        "Lemonade Stand",
                        class_name="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 dark:from-gray-100 to-gray-600 dark:to-gray-400 ml-3 tracking-tight",
                    ),
                    rx.el.span(class_name="hidden"),
                ),
                class_name=rx.cond(
                    UIState.is_sidebar_collapsed,
                    "flex items-center justify-center h-20",
                    "flex items-center h-20 px-6",
                ),
            ),
            rx.el.nav(
                rx.el.div(
                    sidebar_item("Dashboard", "layout-dashboard", href="/"),
                    sidebar_item("Income", "line_chart", href="/income"),
                    sidebar_item("Savings", "piggy-bank", href="/savings"),
                    sidebar_item("Expenses", "receipt", href="/expenses"),
                    sidebar_item("Goals", "target", href="/goals"),
                    class_name="space-y-1 py-6 px-3",
                ),
                rx.el.div(
                    sidebar_item("Settings", "settings", href="/settings"),
                    class_name="mt-auto px-3 pb-6",
                ),
                class_name="flex flex-col h-[calc(100vh-5rem)] justify-between",
            ),
            class_name="h-full bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl",
        ),
        class_name=rx.cond(
            UIState.is_sidebar_collapsed,
            "w-20 border-r border-white/20 dark:border-gray-800/50 shadow-[4px_0_24px_rgba(0,0,0,0.02)] bg-white/80 dark:bg-gray-900/80 h-screen sticky top-0 transition-all duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] z-30",
            "w-56 border-r border-white/20 dark:border-gray-800/50 shadow-[4px_0_24px_rgba(0,0,0,0.02)] bg-white/80 dark:bg-gray-900/80 h-screen sticky top-0 transition-all duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)] z-30",
        ),
    )
