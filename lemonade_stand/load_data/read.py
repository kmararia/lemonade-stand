"""Reads pdf file texts"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from decimal import Decimal as PyDecimal
from pathlib import Path

import numpy as np
import pdfplumber
import polars as pl
import pymupdf.layout
import pymupdf4llm
from dateutil.parser import parse

from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils.exceptions import DataLoadingError

LOGGER = set_up_logger(Path(__file__).stem)
STATEMENT_DATA_SCHEMA = pl.Schema(
    {
        "date": pl.Date(),
        "amount": pl.Float64(),
        "payment": pl.String(),
        "detail": pl.String(),
        "source_file": pl.String(),
        "extract_date": pl.Datetime(time_unit="us", time_zone=None),
    }
)


@dataclass
class Statement:
    """A dataclass for a statement file"""

    file_path: Path
    transactions: pl.LazyFrame = field(init=False)
    engine: str = "pymullm-layout"
    schema: pl.schema.Schema = field(
        default_factory=lambda: STATEMENT_DATA_SCHEMA,
    )

    def __post_init__(self):
        """Post initialization variables"""

        try_engines = ["pdfplumber", "pymullm-llama", "pymullm-layout"]
        used_engines = []

        LOGGER.info("\t> %s", self.file_path.name)

        while True:
            try:
                used_engines.append(self.engine)
                self.transactions = self.get_transactions(
                    pdf_text=self.read_file(read_path=self.file_path),
                )
                break

            except Exception:
                remaining_engines = [x for x in try_engines if x not in used_engines]

                if len(remaining_engines) >= 1:
                    self.engine = remaining_engines[0]
                    LOGGER.error(
                        "Error processing file \t '%s' \n\tSwitching to alternative engine... %s",
                        self.file_path.name,
                        self.engine,
                    )
                else:
                    raise DataLoadingError(
                        f"Unable to process file '{self.file_path.name}'. Skipping processing..."
                    ) from None

    def read_file(self, read_path: Path) -> str:
        """Extracts page text using specified engine"""

        def _read_pdfplumber(pdf_path: Path):
            """Extracts page text using pdfplumber"""

            LOGGER.debug("Reading file using pdfplumber")

            pdf = pdfplumber.open(pdf_path)

            return "\n".join([page.extract_text() for page in pdf.pages])

        def _read_pymullm_llama(pdf_path: Path):
            """Extracts page text using pymullm"""

            LOGGER.debug("Reading file using pymupdf4llm - LlamaMarkdownReader")

            read_obj = pymupdf4llm.LlamaMarkdownReader()
            pdf_data = read_obj.load_data(pdf_path)

            return "\n".join([page.to_dict()["text"] for page in pdf_data])

        def _read_pymullm_layout(pdf_path: Path):
            """Extracts page text using pymullm"""

            LOGGER.debug("Reading file using pymupdf4llm - Layout")

            pdf_doc = pymupdf.open(pdf_path)
            return pymupdf4llm.to_text(pdf_doc, use_ocr=False)

        engine_dict: dict[str, Callable] = {
            "pdfplumber": _read_pdfplumber,
            "pymullm-llama": _read_pymullm_llama,
            "pymullm-layout": _read_pymullm_layout,
        }

        return engine_dict[self.engine](read_path)

    def get_transactions(self, pdf_text: str) -> pl.LazyFrame:
        """Extracts the transaction lines from a string of text

        Returns:
            A polars LazyFrame containing the transaction records

        """
        LOGGER.debug("Getting year of the statement")

        # Define variables
        transaction_matches = []
        file_year = None
        month_patterns = {
            "Jan/January": (
                r"(?:"
                r"Jan(?:uary)?"
                r"|Feb(?:ruary)?"
                r"|Mar(?:ch)?"
                r"|Apr(?:il)?"
                r"|May"
                r"|Jun(?:e)?"
                r"|Jul(?:y)?"
                r"|Aug(?:ust)?"
                r"|Sept(?:ember)?"
                r"|Oct(?:ober)?"
                r"|Nov(?:ember)?"
                r"|Dec(?:ember)?"
                r")"
            ),
            "01": r"\d{2}",
        }

        LOGGER.debug("Scraping transaction lines")

        # Iterate through all the potentail patterns
        for date_format, pattern in month_patterns.items():
            space_patt = r"[^\S\r\n]"

            # Build the statement year pattern
            if date_format == "Jan/January":
                year_pattern = rf"((?:\d{{2}}{space_patt}+{pattern})|(?:{pattern}{space_patt}+\d{{2}}),?{space_patt}*)(\b\d{{4}}\b)"  # Matches: January 31, 2024
            else:
                year_pattern = rf"({pattern}/\d{{2}}/?)(\d{{2}}|\d{{4}})"  # Matches: 04/01/24 or 04/01/2024

            LOGGER.debug("Getting year of the statement")

            # Find the statement file year
            year_search = re.search(re.compile(year_pattern, re.IGNORECASE), pdf_text)
            file_year = year_search.group(2) if year_search else file_year

            # Build the full date pattern conditionally
            if date_format == "Jan/January":
                date_pattern = rf"(?:\d{{2}}{space_patt}+{pattern})|(?:{pattern}{space_patt}+\d{{2}})"  # Matches: 31 January or January 31
            else:
                date_pattern = (
                    rf"{pattern}/\d{{2}}(?:/\d{{2,4}})?"  # Matches: 01/31 or 01/31/2024
                )

            # Find matches iteratively
            LOGGER.debug(
                "Checking date-format %s using pattern: \n\t%s",
                date_format,
                date_pattern,
            )

            amount_pattern = r"[-+$]?\d*[,]?\d+\.\d{2}"
            transactions = re.finditer(
                re.compile(
                    rf"({date_pattern})\s+(?:{date_pattern}\s+)?([\s\S]+?)\s+({amount_pattern})[\b|\s+]({amount_pattern})?",
                    re.IGNORECASE | re.VERBOSE,
                ),
                pdf_text,
            )

            transaction_matches.append([line.groups() for line in transactions])

        # Populate the file year with today's date if none
        file_year = (
            datetime.strptime(file_year, "%y" if len(file_year) == 2 else "%Y")
            if file_year
            else datetime.now()
        )

        # Build dataframe from transaction line matches
        data = [
            (
                parse(row[0], default=file_year).date(),
                PyDecimal(re.sub(r"[,$]", "", row[2])),
                "Credit/Debit Card",
                row[1],
                self.file_path.name,
                datetime.now(),
            )
            for row in transaction_matches[
                # Get list with most transactions captured. Doing this to make sure the optimal date-pattern was captured
                np.argmax([len(x) for x in transaction_matches])
            ]
        ]

        return pl.LazyFrame(
            data=data,
            schema=self.schema,
            orient="row",
        )
