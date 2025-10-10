import os

import pandas as pd
from sclogging import sclogging_main as scl

import_file = os.path.join(os.path.dirname(__file__), "zip_codes.csv")

logger = scl.get_logger()

def load_zip_codes():

    loaded_zip_codes = None

    try:
        loaded_zip_codes = pd.read_csv(import_file, dtype=str)
    except FileNotFoundError:
        logger.error("Zip Code lookup file is missing")

    return loaded_zip_codes

zip_codes = load_zip_codes()

