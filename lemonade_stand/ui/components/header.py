""""""

import reflex as rx


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
                    class_name="flex items-center gap-1 text-xl font-bold text-gray-900 dark:text-gray-100 ml-3 tracking-tight",
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
                        class_name="bg-transparent border-none focus:ring-0 text-sm w-full placeholder:text-gray-500 dark:placeholder:text-gray-400 text-gray-700 dark:text-gray-200 outline-none",
                    ),
                    class_name="hidden md:flex items-center gap-3 bg-white dark:bg-gray-800 px-4 py-2.5 rounded-full w-64 shadow-sm border border-gray-100 dark:border-gray-800 transition-all mr-6",
                ),
                # Color Mode Toggle
                rx.color_mode.button(
                    class_name="mr-6 text-gray-500 dark:text-gray-400 hover:text-indigo-500 dark:hover:text-cyan-400"
                ),
                # Settings Link
                rx.el.a(
                    "Settings",
                    href="/settings",
                    class_name="text-sm font-medium text-gray-700 dark:text-gray-200 hover:text-gray-900 dark:hover:text-gray-200 mr-6 transition-colors",
                ),
                # User Profile
                rx.el.div(
                    rx.el.button(
                        rx.icon("user", size=18, class_name="text-gray-500 mr-2"),
                        rx.el.span(
                            "Kelvin M.",
                            class_name="text-sm font-medium text-gray-700 dark:text-gray-200",
                        ),
                        class_name="flex items-center group cursor-pointer",
                    ),
                ),
                class_name="flex items-center",
            ),
            class_name="flex items-center justify-between h-20 px-8 w-full bg-gray-100 dark:bg-gray-950 border-b-2 border-white dark:border-gray-800 transition-colors",
        ),
        class_name="w-full shrink-0 z-20 my-4",
    )
