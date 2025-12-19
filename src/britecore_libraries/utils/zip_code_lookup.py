from logging import Logger
from pathlib import Path

import pandas as pd

from britecore_libraries import logger

LOGGER: Logger = logger

import_file: Path = Path(Path(__file__).parent / "../resources" / "zip_codes.csv")


def load_zip_codes() -> pd.DataFrame:
    """
    Load zip codes from a CSV file into a pandas DataFrame.

    This function reads zip code data from a specified CSV file and returns it as a pandas DataFrame.
    The function handles the case where the CSV file is missing by logging an error and re-raising
    a FileNotFoundError.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the zip code data with all columns as strings.

    Raises
    ------
    FileNotFoundError
        If the specified CSV file is not found at the given path.
    """

    try:
        loaded_zip_codes = pd.read_csv(import_file, dtype=str)
    except FileNotFoundError:
        LOGGER.error("Zip Code lookup file is missing")
        raise FileNotFoundError

    return loaded_zip_codes


zip_codes = load_zip_codes()
