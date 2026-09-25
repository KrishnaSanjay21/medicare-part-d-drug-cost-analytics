from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path

from src.config import DATABASE
from src.download_data import download_dataset
from src.pipeline import build_database

_BOOTSTRAP_LOCK = threading.Lock()


def ensure_database_ready(
    database_path: Path = DATABASE,
    downloader: Callable[[], Path] = download_dataset,
    builder: Callable[[Path, Path], Path] = build_database,
) -> Path:
    """Create the analytical database on first launch, safely across sessions."""
    if database_path.exists():
        return database_path

    with _BOOTSTRAP_LOCK:
        if database_path.exists():
            return database_path
        source_path = downloader()
        built_path = builder(source_path, database_path)
        if not built_path.exists():
            raise RuntimeError("The pipeline completed without creating the analytical database.")
        return built_path

