"""
Reflex configuration file for lemonade stand app.
"""

import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="lemonade_stand",
    app_module_import="lemonade_stand.app",
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
    frontend_packages=[
        "vite@7.3.3",
        "@tailwindcss/typography",
    ],
)
