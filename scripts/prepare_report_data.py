from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import DATABASE, METADATA_JSON, OUTPUT_DIR, ensure_directories


def rows(connection: sqlite3.Connection, sql: str) -> list[dict]:
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(sql).fetchall()]


def main() -> None:
    ensure_directories()
    with sqlite3.connect(DATABASE) as connection:
        payload = {
            "national_drugs": rows(
                connection,
                """
                SELECT brnd_name, gnrc_name, tot_clms, tot_30day_fills,
                       tot_drug_cst, tot_benes, opioid_drug_flag
                FROM mart_part_d_geo_drug
                WHERE prscrbr_geo_lvl = 'National'
                ORDER BY tot_drug_cst DESC
                """,
            ),
            "states": rows(connection, "SELECT * FROM v_state_summary ORDER BY total_drug_cost DESC"),
            "quality": rows(connection, "SELECT * FROM data_quality_results ORDER BY severity, check_name"),
            "pipeline_runs": rows(connection, "SELECT * FROM pipeline_runs ORDER BY run_id DESC"),
            "metadata": json.loads(METADATA_JSON.read_text(encoding="utf-8")),
        }
    destination = OUTPUT_DIR / "report_data.json"
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()

