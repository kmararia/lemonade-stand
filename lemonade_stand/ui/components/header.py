""""""

import reflex as rx

from lemonade_stand.ui.states.ui_state import UIState


def header() -> rx.Component:
    """"""

    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.el.button(
                    rx.icon(
                        rx.cond(
                            UIState.is_sidebar_collapsed,
                            "panel-left-open",
                            "panel-left-close",
                        ),
                        size=20,
                        class_name="text-gray-600 dark:text-gray-400",
                    ),
                    on_click=UIState.toggle_sidebar,
                    class_name="p-2 rounded-xl hover:bg-gray-100/80 dark:hover:bg-gray-800/80 transition-all focus:ring-2 focus:ring-indigo-100 outline-none active:scale-95",
                    title="Toggle Sidebar",
                ),
                rx.el.div(
                    rx.icon("search", size=18, class_name="text-gray-400"),
                    rx.el.input(
                        placeholder="Search anything...",
                        class_name="bg-transparent border-none focus:ring-0 text-sm w-full placeholder:text-gray-400 text-gray-700 dark:text-gray-200 outline-none",
                    ),
                    class_name="hidden md:flex items-center gap-3 bg-gray-50/80 dark:bg-gray-900/50 px-4 py-2 rounded-xl w-64 border border-transparent focus-within:border-indigo-200 dark:focus-within:border-cyan-700/50 focus-within:bg-white dark:focus-within:bg-gray-900/80 focus-within:shadow-sm transition-all duration-300 ml-4",
                ),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.div(
                    rx.color_mode.button(
                        class_name="mr-4 text-gray-500 dark:text-gray-400 hover:text-indigo-500 dark:hover:text-cyan-400"
                    ),
                    rx.el.button(
                        rx.image(
                            src="https://api.dicebear.com/9.x/notionists/svg?seed=Felix",
                            class_name="w-9 h-9 rounded-full bg-indigo-50 dark:bg-cyan-900/30 border-2 border-white dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Alex Finance",
                                class_name="text-sm font-semibold text-gray-700 dark:text-gray-200 leading-none group-hover:text-indigo-600 dark:group-hover:text-cyan-400 transition-colors",
                            ),
                            rx.el.p(
                                "Admin",
                                class_name="text-xs text-gray-500 dark:text-gray-400 mt-1 leading-none",
                            ),
                            class_name="hidden sm:block text-right",
                        ),
                        rx.icon(
                            "chevron-down",
                            size=16,
                            class_name="text-gray-400 group-hover:text-indigo-500 dark:group-hover:text-cyan-400 transition-colors",
                        ),
                        class_name="flex items-center gap-3 pl-4 border-l border-gray-200/60 dark:border-gray-700/60 ml-2 group cursor-pointer",
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex items-center justify-between h-20 px-6 bg-white/70 dark:bg-gray-800/50 backdrop-blur-xl border-b border-white/50 dark:border-gray-700/50 shadow-sm",
        ),
        class_name="sticky top-0 z-20 w-full",
    )
