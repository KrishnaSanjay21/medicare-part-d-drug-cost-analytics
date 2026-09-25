from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

from src.config import DATA_YEAR, DATABASE, ROOT, ensure_directories

REQUIRED_COLUMNS = {
    "Prscrbr_Geo_Lvl",
    "Prscrbr_Geo_Cd",
    "Prscrbr_Geo_Desc",
    "Brnd_Name",
    "Gnrc_Name",
    "Tot_Prscrbrs",
    "Tot_Clms",
    "Tot_30day_Fills",
    "Tot_Drug_Cst",
    "Tot_Benes",
    "LIS_Bene_Cst_Shr",
    "NonLIS_Bene_Cst_Shr",
    "Opioid_Drug_Flag",
    "Opioid_LA_Drug_Flag",
    "Antbtc_Drug_Flag",
    "Antpsyct_Drug_Flag",
}

NUMERIC_COLUMNS = [
    "tot_prscrbrs",
    "tot_clms",
    "tot_30day_fills",
    "tot_drug_cst",
    "tot_benes",
    "ge65_tot_clms",
    "ge65_tot_30day_fills",
    "ge65_tot_drug_cst",
    "ge65_tot_benes",
    "lis_bene_cst_shr",
    "nonlis_bene_cst_shr",
]

STATE_REFERENCE = [
    ("01", "AL"), ("02", "AK"), ("04", "AZ"), ("05", "AR"), ("06", "CA"),
    ("08", "CO"), ("09", "CT"), ("10", "DE"), ("11", "DC"), ("12", "FL"),
    ("13", "GA"), ("15", "HI"), ("16", "ID"), ("17", "IL"), ("18", "IN"),
    ("19", "IA"), ("20", "KS"), ("21", "KY"), ("22", "LA"), ("23", "ME"),
    ("24", "MD"), ("25", "MA"), ("26", "MI"), ("27", "MN"), ("28", "MS"),
    ("29", "MO"), ("30", "MT"), ("31", "NE"), ("32", "NV"), ("33", "NH"),
    ("34", "NJ"), ("35", "NM"), ("36", "NY"), ("37", "NC"), ("38", "ND"),
    ("39", "OH"), ("40", "OK"), ("41", "OR"), ("42", "PA"), ("44", "RI"),
    ("45", "SC"), ("46", "SD"), ("47", "TN"), ("48", "TX"), ("49", "UT"),
    ("50", "VT"), ("51", "VA"), ("53", "WA"), ("54", "WV"), ("55", "WI"),
    ("56", "WY"), ("66", "GU"), ("69", "MP"), ("72", "PR"), ("78", "VI"),
    ("9A", "AA"), ("9B", "AE"), ("9C", "AP"), ("9D", "UN"), ("9E", "FC"),
]


def snake_case(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", value.strip())
    return value.strip("_").lower()


def normalize_source(frame: pd.DataFrame, data_year: int = DATA_YEAR) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"CMS source is missing required columns: {sorted(missing)}")

    clean = frame.copy()
    clean.columns = [snake_case(column) for column in clean.columns]
    clean["data_year"] = int(data_year)
    clean["prscrbr_geo_cd"] = clean["prscrbr_geo_cd"].fillna("").astype(str).str.strip()
    clean["prscrbr_geo_lvl"] = clean["prscrbr_geo_lvl"].fillna("").astype(str).str.strip()
    clean["prscrbr_geo_desc"] = clean["prscrbr_geo_desc"].fillna("").astype(str).str.strip()
    clean["brnd_name"] = clean["brnd_name"].fillna("Unknown").astype(str).str.strip()
    clean["gnrc_name"] = clean["gnrc_name"].fillna("Unknown").astype(str).str.strip()

    for column in NUMERIC_COLUMNS:
        if column in clean.columns:
            clean[column] = pd.to_numeric(clean[column], errors="coerce")

    flag_columns = [
        "ge65_sprsn_flag",
        "ge65_bene_sprsn_flag",
        "opioid_drug_flag",
        "opioid_la_drug_flag",
        "antbtc_drug_flag",
        "antpsyct_drug_flag",
    ]
    for column in flag_columns:
        if column in clean.columns:
            clean[column] = clean[column].fillna("").astype(str).str.strip().str.upper()
    return clean


def run_sql_script(connection: sqlite3.Connection, path: Path) -> None:
    connection.executescript(path.read_text(encoding="utf-8"))


def build_database(csv_path: Path, database_path: Path = DATABASE) -> Path:
    """Load the official CSV into SQLite and create analytical marts."""
    ensure_directories()
    source = pd.read_csv(csv_path, low_memory=False)
    clean = normalize_source(source)

    if database_path.exists():
        database_path.unlink()
    with sqlite3.connect(database_path) as connection:
        clean.to_sql("raw_part_d_geo_drug", connection, index=False, if_exists="replace")
        pd.DataFrame(STATE_REFERENCE, columns=["state_fips", "state_code"]).to_sql(
            "state_reference", connection, index=False, if_exists="replace"
        )
        run_sql_script(connection, ROOT / "sql" / "01_transform.sql")
        run_sql_script(connection, ROOT / "sql" / "02_quality_checks.sql")
        connection.execute(
            "INSERT INTO pipeline_runs(run_at_utc, source_rows, data_year, status) "
            "VALUES(datetime('now'), ?, ?, 'SUCCESS')",
            (len(clean), DATA_YEAR),
        )
        connection.commit()
    return database_path
