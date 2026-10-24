import csv
from pathlib import Path

from streamstats.report import csv_report


def test_csv_report(tmp_path: Path) -> None:
    """Проверка создания CSV-отчёта"""

    filepath = tmp_path / "report.csv"

    report = {
        "total": 2,
        "skipped_lines": 0,
        "first_timestamp": "2026-10-22T10:00:00Z",
        "last_timestamp": "2026-10-22T10:05:00Z",
        "cnt_level": {"INFO": 1, "ERROR": 1},
        "cnt_source": {"auth": 1, "database": 1},
        "top_errors": [
            {"source": "database", "level": "ERROR", "count": 1}
        ],
    }

    csv_report(report, filepath)

    with open(filepath, encoding="utf-8", newline="") as file:
        rows = list(csv.reader(file))

    assert rows[0] == ["Общая статистика"]
    assert rows[1] == ["total", "2"]
    assert ["INFO", "1"] in rows
    assert ["skipped_lines", "0"] in rows
    assert ["Топ ошибок"] in rows
    assert ["database", "ERROR", "1"] in rows
    assert len(rows) == 19
