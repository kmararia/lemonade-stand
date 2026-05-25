"""
Utilities to help download files and unzip utilities
"""

import shutil
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import certifi
import urllib3
from tqdm import tqdm

from lemonade_stand.config import AppDir
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
DIRECTORIES = AppDir()


def unzip_file(zip_path: Path, extract_to: Path = None) -> None:
    """
    Unzips a file to a specified location.

    Args:
        zip_path: Path to the zip file
        extract_to (Optional[Path]): Path to extract the contents of the zip file to
    """

    if zip_path.suffix == ".zip":
        unzip_dir = (
            (extract_to / zip_path.stem)
            if extract_to
            else (zip_path.parent / zip_path.stem)
        )

        # Clean up any existing directory before unzipping
        shutil.rmtree(unzip_dir, ignore_errors=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(unzip_dir)

    else:
        raise ValueError(f"Unsupported file type: {zip_path.suffix}")

    return unzip_dir


def download_data(download_url: str, file_name: str | None = None) -> Path:
    """
    Download a file from a URL and save it to the local filesystem.

    Args:
        download_url (str): The URL of the file to download.
        file_name (str | None, optional): The name to save the downloaded file as. If None, the name will be derived from the URL.
    Returns:
        Path: The path to the downloaded file.
    """

    # Set up paths
    download_url = urlparse(download_url)
    file_name = Path(download_url.path).name if file_name is None else file_name
    download_file = DIRECTORIES.root_dir / "downloads" / file_name

    if download_file.exists():
        download_file.unlink()
    else:
        download_file.parent.mkdir(parents=True, exist_ok=True)

    LOGGER.debug(
        "Downloading file \n\tfrom: %s \n\tto: %s", download_url.geturl(), download_file
    )

    # Create pool manager and set up request
    http = urllib3.PoolManager(ca_certs=certifi.where())
    request = http.request("GET", download_url.geturl(), preload_content=False)

    chunk_size = 10 * (1024 * 1024)
    file_size = (
        int(request.headers["Content-Length"])
        if "Content-Length" in request.headers
        else None
    )

    # Download the file in chunks
    with (
        download_file.open(mode="wb") as file,
        tqdm(
            bar_format="{l_bar}{bar} | [{elapsed}] {n_fmt}/{total_fmt}",
            desc=f"Downloading {file_name}",
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

    request.release_conn()

    return download_file
