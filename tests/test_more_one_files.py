from pathlib import Path

from streamstats.__main__ import read_events
from streamstats.analysis import analyze
from streamstats.models import ParseStatistic
from streamstats.parsers import parse_jsonl


def test_multiple_jsonl_files(tmp_path: Path) -> None:
    """Проверка общей статистики по двум JSONL-файлам"""

    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"

    first.write_text(
        '{"timestamp":"2026-10-22T10:00:00Z",'
        '"level":"INFO","source":"auth","message":"OK"}\n'
        '{"timestamp":"2026-10-22T10:05:00Z",'
        '"level":"ERROR","source":"database","message":"Failed"}\n',
        encoding="utf-8",
    )

    second.write_text(
        '{"timestamp":"2026-10-22T10:10:00Z",'
        '"level":"CRITICAL","source":"auth","message":"Alert"}\n',
        encoding="utf-8",
    )

    stats = ParseStatistic()

    events = read_events(
        [str(first), str(second)],
        parse_jsonl,
        False,
        stats,
    )

    result = analyze(events)

    assert result["total"] == 3
    assert result["cnt_level"]["INFO"] == 1
    assert result["cnt_level"]["ERROR"] == 1
    assert result["cnt_level"]["CRITICAL"] == 1
    assert result["cnt_source"]["auth"] == 2
    assert result["cnt_source"]["database"] == 1
    assert stats.skip_lines == 0
