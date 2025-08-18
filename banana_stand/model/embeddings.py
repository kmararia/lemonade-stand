"""
Set up GloVe zipped_file
Data pulled from:
    --> https://nlp.stanford.edu/projects/glove/
"""

import json
import zipfile
from pathlib import Path

import numpy as np
import urllib3
from tqdm import tqdm

from banana_stand import __version__
from banana_stand.app_config import AppDir
from banana_stand.utils import VersionMismatchError
from banana_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)

CONFIGS = {
    "version": __version__,
    "embeddings url": "https://nlp.stanford.edu/data/wordvecs/glove.2024.dolma.300d.zip",
}


def check_version(zipped_file: Path):
    """
    Validates that the embedding data exists and is upto date
    """

    config_file = zipped_file.parent / "metadata.json"

    def _write_config():
        with config_file.open("w") as file:
            json.dump(CONFIGS, file, indent=4)

    # Confirm if we need to re-download data
    if (not zipped_file.exists()) or (not config_file.exists()):
        _write_config()
        return True

    else:
        # Check if recent version exists
        try:
            config_dict = json.load(config_file.open("r"))

            if config_dict["version"] == config_dict["version"]:
                return False
            else:
                raise VersionMismatchError("Non-matching embeddings versions")

        except VersionMismatchError:
            _write_config()
            return True


def get_glove_embeddings(dirs: AppDir):
    """
    Prepare the GloVe embeddings datasets
    """

    # Set up write out file
    zipped_file = dirs.root_dir / "shared" / "schema" / "glove_embeddings.zip"
    zipped_file.parent.mkdir(parents=True, exist_ok=True)

    # Download data in stream chunks if needed
    if check_version(zipped_file):
        LOGGER.debug("Downloading Glove embeddings")

        # Create pool manager and set up request
        http = urllib3.PoolManager()
        request = http.request("GET", CONFIGS["embeddings url"], preload_content=False)

        chunk_size = 10 * (1024 * 1024)
        file_size = (
            int(request.headers["Content-Length"])
            if "Content-Length" in request.headers
            else None
        )

        # Download the file in chunks
        with (
            zipped_file.open(mode="wb") as file,
            tqdm(
                bar_format="{l_bar}{bar} | [{elapsed}] {n_fmt}/{total_fmt}",
                desc="Downloading embeddings",
                colour="blue",
                total=file_size,
                unit_divisor=1024,
                unit_scale=True,
                unit="miB",
            ) as progress,
        ):
            for chunk in request.stream(chunk_size):
                file.write(chunk)
                progress.update(len(chunk))

        # Free the connection
        request.release_conn()

    # Unzip the file
    with zipfile.ZipFile(zipped_file, "r") as zip_ref:
        for file_name in zip_ref.namelist():
            # Read the contents of each file and save
            with zip_ref.open(file_name) as file:
                for line in file:
                    line_parts = line.decode("utf-8").strip().split()

                    # Split the words and vector
                    yield (
                        line_parts[0],  # word
                        np.array(line_parts[1:], dtype=np.float32),  # vector embeddings
                    )
