"""
Banana-stand entry point.
"""

import banana_stand

if __name__ == "__main__":
    # Configure application
    app = banana_stand.create_app()

    # Boot up application server
    app.run(port=8050, debug=True)
