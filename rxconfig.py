"""
Reflex configuration file for lemonade stand app.
"""

import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="lemonade_stand",
    app_module_import="lemonade_stand.app",
    api_url="https://lemonade-stand-jj9j.onrender.com",
    cors_allowed_origins=["*"],
    disable_plugins=[SitemapPlugin],
    plugins=[
        rx.plugins.RadixThemesPlugin(theme=rx.theme(appearance="inherit")),
        rx.plugins.TailwindV3Plugin(
            config={
                "plugins": [
                    "@tailwindcss/typography",
                ],
                "darkMode": "class",
                "theme": {
                    "extend": {},
                },
            }
        ),
    ],
)
