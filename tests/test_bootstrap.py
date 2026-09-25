from pathlib import Path

from src.bootstrap import ensure_database_ready


def test_bootstrap_builds_missing_database(tmp_path: Path):
    database = tmp_path / "processed" / "analytics.sqlite"
    source = tmp_path / "source.csv"
    calls: list[str] = []

    def fake_download() -> Path:
        calls.append("download")
        source.write_text("published,cms,data\n", encoding="utf-8")
        return source

    def fake_build(source_path: Path, database_path: Path) -> Path:
        calls.append("build")
        assert source_path == source
        database_path.parent.mkdir(parents=True, exist_ok=True)
        database_path.write_bytes(b"sqlite-test")
        return database_path

    result = ensure_database_ready(database, fake_download, fake_build)

    assert result == database
    assert result.exists()
    assert calls == ["download", "build"]


def test_bootstrap_reuses_existing_database(tmp_path: Path):
    database = tmp_path / "analytics.sqlite"
    database.write_bytes(b"existing")

    def unexpected_download() -> Path:
        raise AssertionError("Existing deployments must not download again")

    result = ensure_database_ready(database, unexpected_download)
    assert result == database

