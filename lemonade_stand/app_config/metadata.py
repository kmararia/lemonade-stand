"""
Holds metadata configurations for different module steps
"""

import importlib.metadata
from datetime import datetime

__version__ = importlib.metadata.version("banana-stand")

USER_CONFIG = {
    "app-version": __version__,
    "last-updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "export-flag": False,
}

MODEL_CONFIG = {
    "version": __version__,
    "embeddings_url": "https://nlp.stanford.edu/data/wordvecs/glove.2024.dolma.300d.zip",
}
