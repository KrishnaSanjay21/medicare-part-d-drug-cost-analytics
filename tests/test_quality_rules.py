import sqlite3

from src.config import DATABASE


def test_production_quality_checks_pass_when_database_exists():
    if not DATABASE.exists():
        return
    with sqlite3.connect(DATABASE) as connection:
        failed = connection.execute(
            "SELECT COUNT(*) FROM data_quality_results "
            "WHERE severity = 'Critical' AND status <> 'PASS'"
        ).fetchone()[0]
    assert failed == 0
