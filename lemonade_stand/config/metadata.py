"""
Holds metadata configurations for different module steps
"""

import importlib.metadata
from datetime import datetime
from pathlib import Path

import lemonade_stand

__version__ = importlib.metadata.version("lemonade-stand")

USER_CONFIG = {
    "app-version": __version__,
    "last-updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "statement-directory": str(
        Path(lemonade_stand.__file__).parents[1] / "tests" / "data" / "statements"
    ),
    "always-refresh-data": False,
    "always-request-login": True,
}

MODEL_CONFIG = {
    "version": __version__,
    "embeddings_url": "https://nlp.stanford.edu/data/wordvecs/glove.2024.dolma.300d.zip",
}
