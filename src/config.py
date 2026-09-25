from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = ROOT / "outputs"

DATA_YEAR = 2024
DATASET_VERSION_ID = "9b4c142c-69cc-4a96-a09a-7cf2ba7f5816"
DATASET_PAGE = (
    "https://data.cms.gov/provider-summary-by-type-of-service/"
    "medicare-part-d-prescribers/"
    "medicare-part-d-prescribers-by-geography-and-drug"
)
DATASET_URL = (
    "https://data.cms.gov/sites/default/files/2026-05/"
    "3e80b44e-5a87-4414-959a-b6a7c8c18720/"
    "MUP_DPR_RY26_P04_V10_DY24_Geo.csv"
)
RAW_CSV = RAW_DIR / f"cms_part_d_geography_drug_{DATA_YEAR}.csv"
METADATA_JSON = RAW_DIR / "source_metadata.json"
DATABASE = PROCESSED_DIR / "cms_part_d_analytics.sqlite"


def ensure_directories() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, OUTPUT_DIR):
        path.mkdir(parents=True, exist_ok=True)

