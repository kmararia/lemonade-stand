"""Reads pdf file texts"""

from pathlib import Path

import pdfplumber
import pymupdf4llm

from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


def read_pdfplumber(pdf_path: Path):
    """Extracts page text using pdfplumber"""
    LOGGER.info("Reading file using pdfplumber")

    # Initialize pdf read object
    pdf = pdfplumber.open(pdf_path)

    # Return list of page strings
    return [page.extract_text() for page in pdf.pages]


def read_pymullm(pdf_path: Path):
    """Extracts page text using pymullm"""
    LOGGER.info("Reading file using pymupdf4llm")

    # Initialize pdf read object
    read_obj = pymupdf4llm.LlamaMarkdownReader()
    pdf_data = read_obj.load_data(pdf_path)

    # Return list of page strings
    return [page.to_dict()["text"] for page in pdf_data]
