from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from src.config import (
    DATASET_PAGE,
    DATASET_URL,
    DATASET_VERSION_ID,
    DATA_YEAR,
    METADATA_JSON,
    RAW_CSV,
    ensure_directories,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_dataset(force: bool = False) -> Path:
    """Download the official CMS CSV and write reproducibility metadata."""
    ensure_directories()
    if RAW_CSV.exists() and not force:
        return RAW_CSV

    temporary = RAW_CSV.with_suffix(".download")
    request = urllib.request.Request(
        DATASET_URL,
        headers={"User-Agent": "cms-part-d-portfolio-project/1.0"},
    )
    with urllib.request.urlopen(request, timeout=180) as response, temporary.open("wb") as target:
        shutil.copyfileobj(response, target)
    temporary.replace(RAW_CSV)

    metadata = {
        "dataset": "Medicare Part D Prescribers - by Geography and Drug",
        "publisher": "Centers for Medicare & Medicaid Services",
        "data_year": DATA_YEAR,
        "dataset_version_id": DATASET_VERSION_ID,
        "dataset_page": DATASET_PAGE,
        "download_url": DATASET_URL,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_name": RAW_CSV.name,
        "file_size_bytes": RAW_CSV.stat().st_size,
        "sha256": sha256_file(RAW_CSV),
        "license": "U.S. Government public-use data",
    }
    METADATA_JSON.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return RAW_CSV


if __name__ == "__main__":
    print(download_dataset())

