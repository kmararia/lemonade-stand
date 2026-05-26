""""""

import reflex as rx

from lemonade_stand.ui.components.header import header
from lemonade_stand.ui.components.sidebar import sidebar
from lemonade_stand.ui.pages.budgets import budgets_page
from lemonade_stand.ui.pages.dashboard import dashboard_content


def index() -> rx.Component:
    """"""

    def background_pattern() -> rx.Component:
        """ """
        return rx.el.div(
            rx.el.div(
                class_name="absolute top-0 left-0 w-full h-96 bg-gradient-to-br from-indigo-100/40 via-purple-100/30 to-transparent -z-10"
            ),
            rx.el.div(
                class_name="absolute top-[-50px] right-[-50px] w-96 h-96 bg-purple-200/30 rounded-full blur-3xl -z-10 mix-blend-multiply filter opacity-70 animate-blob"
            ),
            rx.el.div(
                class_name="absolute top-[-50px] left-[-50px] w-96 h-96 bg-indigo-200/30 rounded-full blur-3xl -z-10 mix-blend-multiply filter opacity-70 animate-blob animation-delay-2000"
            ),
            class_name="fixed inset-0 overflow-hidden pointer-events-none dark:hidden",
        )

    return rx.el.div(
        background_pattern(),
        sidebar(),
        rx.el.div(
            header(),
            rx.el.main(
                dashboard_content(),
                class_name="flex-1 p-6 md:p-8 overflow-y-auto scroll-smooth",
            ),
            class_name="flex-1 flex flex-col h-screen overflow-hidden bg-gray-50/30 dark:bg-transparent backdrop-blur-sm",
        ),
        class_name="flex h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-300 font-['Inter'] selection:bg-indigo-100 dark:selection:bg-cyan-900 selection:text-indigo-900 dark:selection:text-cyan-100",
    )


# Build and deploy the app
app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
)

app.add_page(index, route="/")
app.add_page(budgets_page, route="/budgets")
