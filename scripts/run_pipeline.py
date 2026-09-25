from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import DATABASE
from src.download_data import download_dataset
from src.pipeline import build_database


def main() -> None:
    source = download_dataset()
    database = build_database(source)
    print(f"Source: {source}")
    print(f"Database: {database}")
    print(f"Ready: {database == DATABASE and database.exists()}")


if __name__ == "__main__":
    main()
