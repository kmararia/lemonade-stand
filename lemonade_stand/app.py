""""""

import reflex as rx

from lemonade_stand.ui.components.header import header
from lemonade_stand.ui.components.sidebar import sidebar
from lemonade_stand.ui.pages.expense import expense_page
from lemonade_stand.ui.pages.home import home_content
from lemonade_stand.ui.states.ui_state import UIState


def index() -> rx.Component:
    """"""
    return rx.el.div(
        # Inner floating APP
        rx.el.div(
            header(),
            rx.el.div(
                sidebar(),
                rx.el.main(
                    home_content(),
                    # The main content area blends into the background
                    class_name="flex-1 p-6 md:p-8 overflow-y-auto scroll-smooth",
                ),
                class_name="flex-1 flex overflow-hidden",
            ),
            class_name="flex flex-col w-full h-full bg-gray-100 dark:bg-gray-950 text-gray-900 dark:text-gray-300 rounded-[2.5rem] shadow-2xl overflow-hidden border border-gray-100 dark:border-gray-800",
        ),
        # Grayed out bakground
        class_name="flex h-screen w-screen bg-gray-300/60 dark:bg-gray-900 p-4 md:p-6 lg:p-8",
    )


# Build and deploy the app
app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;600;700&text=0123456789.%2C%24%25%2B-&display=swap",
        "https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap",
        "https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,100..900;1,100..900&display=swap",
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
        "/fonts.css",
    ],
)

app.add_page(index, route="/")  # , on_load=DataState.load_shared_data)
app.add_page(expense_page, route="/expenses", on_load=UIState.collapse_sidebar)
