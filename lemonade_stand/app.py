"""
Main application module
"""

import dash
from dash import Dash


def create_app():
    """
    Main application function
    """

    # Set up custom web style
    style_sheets = [
        {
            "href": (
                "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap"
            ),
            "rel": "stylesheet",
        }
    ]

    # Initialize web application
    app = Dash(
        name=__name__,
        use_pages=True,
        external_stylesheets=style_sheets,
        suppress_callback_exceptions=True,
    )

    app.layout = dash.page_container

    return app.run(port=8050, debug=True)
