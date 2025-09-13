"""
Lemonade-stand entry point.
"""

import lemonade_stand

if __name__ == "__main__":
    # Configure application
    app = lemonade_stand.create_app()

    # Boot up application server
    app.run(port=8050, debug=True)
