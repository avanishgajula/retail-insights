import logging
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve

import pandas as pd

DATASET_URL = (
    "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"
)
RAW_DATA_PATH = Path("data/raw/source_data.csv")

logger = logging.getLogger(__name__)


def read_raw_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Read raw retail data from a CSV file."""
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found: {path}")

    return pd.read_csv(path)


def download_csv(url: str = DATASET_URL, output_path: Path = RAW_DATA_PATH) -> Path:
    """Download a CSV file from a public URL and save it locally."""
    logger.info("Starting CSV download from %s", url)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        urlretrieve(url, output_path)
    except (HTTPError, URLError, OSError) as error:
        logger.exception("Failed to download CSV to %s", output_path)
        raise RuntimeError(f"Could not download CSV from {url}") from error

    logger.info("Successfully saved CSV to %s", output_path)
    return output_path


def main() -> None:
    """Run the ingestion step from the command line."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    download_csv()


if __name__ == "__main__":
    main()
