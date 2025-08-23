"""
Set up GloVe zipped_file
Data pulled from:
    --> https://nlp.stanford.edu/projects/glove/
"""

import zipfile
from pathlib import Path

import numpy as np
import urllib3
from tqdm import tqdm

from banana_stand.app_config import AppDir
from banana_stand.app_config import MetaData
from banana_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)

GLOVE_METADATA = MetaData("model")
DIRECTORIES = AppDir()


def get_glove_embeddings():
    """
    Prepare the GloVe embeddings datasets
    """

    configs = GLOVE_METADATA.dot_data

    # Set up write out file
    zipped_file = DIRECTORIES.root_dir / "shared" / "schema" / "glove_embeddings.zip"
    zipped_file.parent.mkdir(parents=True, exist_ok=True)

    # Download data in stream chunks if needed
    if (not zipped_file.exists()) or GLOVE_METADATA.refresh_flag:
        LOGGER.debug("Downloading Glove embeddings")

        # Create pool manager and set up request
        http = urllib3.PoolManager()
        request = http.request("GET", configs.embeddings_url, preload_content=False)

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
