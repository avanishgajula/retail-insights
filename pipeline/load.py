import logging
import sqlite3
from pathlib import Path

import pandas as pd

CLEAN_DATA_PATH = Path("data/processed/clean_data.csv")
DATABASE_PATH = Path("analytics.db")
TABLE_NAME = "sales_data"

logger = logging.getLogger(__name__)


def read_clean_data(path: Path = CLEAN_DATA_PATH) -> pd.DataFrame:
    """Read the cleaned data CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Cleaned data file not found: {path}")

    return pd.read_csv(path)


def load_to_sqlite(
    data_path: Path = CLEAN_DATA_PATH,
    database_path: Path = DATABASE_PATH,
    table_name: str = TABLE_NAME,
) -> None:
    """Load cleaned CSV data into a SQLite table."""
    logger.info("Starting load from %s into %s", data_path, database_path)
    data = read_clean_data(data_path)

    try:
        with sqlite3.connect(database_path) as connection:
            data.to_sql(table_name, connection, if_exists="replace", index=False)
    except sqlite3.Error as error:
        logger.exception("Failed to load data into SQLite")
        raise RuntimeError("Could not load cleaned data into SQLite") from error

    logger.info("Loaded %s rows into table %s", len(data), table_name)


def main() -> None:
    """Run the load step from the command line."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    load_to_sqlite()


if __name__ == "__main__":
    main()
