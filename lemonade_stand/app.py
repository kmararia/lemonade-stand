""""""

import reflex as rx

from lemonade_stand.ui.pages.expense import expense_page
from lemonade_stand.ui.pages.home import home_content
from lemonade_stand.ui.pages.income import income_page
from lemonade_stand.ui.pages.savings import savings_page
from lemonade_stand.ui.states.income_state import DataState

# Build and deploy the app
app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;600;700&text=0123456789.%2C%24%25%2B-&display=swap",
        "https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap",
        "https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,100..900;1,100..900&display=swap",
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
        "/styles.css",
    ],
)

app.add_page(home_content, route="/", on_load=DataState.load_shared_data)
app.add_page(income_page, route="/income", on_load=DataState.load_shared_data)
app.add_page(savings_page, route="/savings", on_load=DataState.load_shared_data)
app.add_page(expense_page, route="/expenses", on_load=DataState.load_shared_data)
