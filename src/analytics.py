from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.config import DATABASE


def query(sql: str, params: tuple = (), database: Path = DATABASE) -> pd.DataFrame:
    with sqlite3.connect(database) as connection:
        return pd.read_sql_query(sql, connection, params=params)


def executive_metrics(database: Path = DATABASE) -> pd.Series:
    frame = query(
        """
        SELECT data_year,
               SUM(tot_clms) AS total_claims,
               SUM(tot_30day_fills) AS total_30day_fills,
               SUM(tot_drug_cst) AS total_drug_cost,
               SUM(tot_benes) AS total_beneficiary_records,
               COUNT(DISTINCT brnd_name || '|' || gnrc_name) AS distinct_drugs,
               SUM(tot_drug_cst) / NULLIF(SUM(tot_clms), 0) AS cost_per_claim,
               SUM(CASE WHEN opioid_drug_flag = 'Y' THEN tot_drug_cst ELSE 0 END)
                 / NULLIF(SUM(tot_drug_cst), 0) AS opioid_cost_share
        FROM mart_part_d_geo_drug
        WHERE prscrbr_geo_lvl = 'National'
        GROUP BY data_year
        """,
        database=database,
    )
    return frame.iloc[0]


def top_drugs(limit: int = 15, database: Path = DATABASE) -> pd.DataFrame:
    return query(
        """
        SELECT brnd_name, gnrc_name, tot_clms, tot_30day_fills, tot_drug_cst,
               cost_per_claim, tot_benes, opioid_drug_flag
        FROM mart_part_d_geo_drug
        WHERE prscrbr_geo_lvl = 'National'
        ORDER BY tot_drug_cst DESC
        LIMIT ?
        """,
        (limit,),
        database,
    )


def state_summary(database: Path = DATABASE) -> pd.DataFrame:
    return query("SELECT * FROM v_state_summary ORDER BY total_drug_cost DESC", database=database)


def quality_results(database: Path = DATABASE) -> pd.DataFrame:
    return query("SELECT * FROM data_quality_results ORDER BY severity, check_name", database=database)

