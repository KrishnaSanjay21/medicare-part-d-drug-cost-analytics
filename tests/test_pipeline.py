import sqlite3

import pandas as pd
import pytest

from src.pipeline import normalize_source


@pytest.fixture
def cms_frame():
    return pd.DataFrame(
        [
            {
                "Prscrbr_Geo_Lvl": "National",
                "Prscrbr_Geo_Cd": "",
                "Prscrbr_Geo_Desc": "National",
                "Brnd_Name": "Example Drug",
                "Gnrc_Name": "example generic",
                "Tot_Prscrbrs": "10",
                "Tot_Clms": "100",
                "Tot_30day_Fills": "110.5",
                "Tot_Drug_Cst": "2500.00",
                "Tot_Benes": "50",
                "GE65_Sprsn_Flag": "",
                "GE65_Tot_Clms": "80",
                "GE65_Tot_30day_Fills": "90",
                "GE65_Tot_Drug_Cst": "2000",
                "GE65_Bene_Sprsn_Flag": "",
                "GE65_Tot_Benes": "40",
                "LIS_Bene_Cst_Shr": "50",
                "NonLIS_Bene_Cst_Shr": "100",
                "Opioid_Drug_Flag": "N",
                "Opioid_LA_Drug_Flag": "N",
                "Antbtc_Drug_Flag": "N",
                "Antpsyct_Drug_Flag": "N",
            }
        ]
    )


def test_normalize_source_converts_numeric_columns(cms_frame):
    result = normalize_source(cms_frame)
    assert result.loc[0, "tot_clms"] == 100
    assert result.loc[0, "tot_drug_cst"] == 2500
    assert result.loc[0, "data_year"] == 2024


def test_normalize_source_requires_documented_fields(cms_frame):
    with pytest.raises(ValueError, match="missing required columns"):
        normalize_source(cms_frame.drop(columns=["Tot_Clms"]))


def test_sqlite_metric_definition(cms_frame):
    result = normalize_source(cms_frame)
    with sqlite3.connect(":memory:") as connection:
        result.to_sql("source", connection, index=False)
        value = connection.execute("SELECT SUM(tot_drug_cst) / SUM(tot_clms) FROM source").fetchone()[0]
    assert value == 25.0

