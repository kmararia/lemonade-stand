"""
Reflex configuration file for lemonade stand app.
"""

import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="lemonade_stand",
    app_module_import="lemonade_stand.app",
    # db_url="",
    disable_plugins=[SitemapPlugin],
    plugins=[
        rx.plugins.TailwindV3Plugin(
            config={
                "plugins": [
                    "@tailwindcss/typography",
                ],
            }
        )
    ],
)
