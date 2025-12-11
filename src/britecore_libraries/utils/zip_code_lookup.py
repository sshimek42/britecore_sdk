from pathlib import Path
import pandas as pd
from britecore_libraries import logger

LOGGER = logger

import_file = Path(Path(__file__).parent / "../resources" / "zip_codes.csv")


def load_zip_codes():
    loaded_zip_codes = None

    try:
        loaded_zip_codes = pd.read_csv(import_file, dtype=str)
    except FileNotFoundError:
        LOGGER.error("Zip Code lookup file is missing")

    return loaded_zip_codes


zip_codes = load_zip_codes()
