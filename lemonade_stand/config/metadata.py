"""Holds metadata configurations for different module steps"""

import importlib.metadata
from datetime import datetime
from pathlib import Path

import lemonade_stand

__version__ = importlib.metadata.version("lemonade-stand")

BASE_CONFIG = {
    "app-version": __version__,
    "last-updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "data": {
        "always-refresh-data": True,
        "statement-dir": (
            Path(lemonade_stand.__file__).parents[1] / "tests" / "data" / "statements"
        ),
    },
    "model": {
        "embeddings_url": "https://nlp.stanford.edu/data/wordvecs/glove.2024.dolma.300d.zip",
        "training-file": (
            Path(lemonade_stand.__file__).parents[1]
            / "tests"
            / "model"
            / "training.csv"
        ),
    },
    "ui": {"always-skip-login": False, "dark-mode": True},
}
