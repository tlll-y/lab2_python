from streamstats.analysis import analyze
from streamstats.models import Event


def test_analyze_counts() -> None:
    """Проверка количества событий по уровням и источникам"""

    events = [
        Event(
            timestamp="2026-10-22T10:00:00Z",
            level="INFO",
            source="auth",
            message="User logged in",
        ),
        Event(
            timestamp="2026-10-22T10:05:00Z",
            level="ERROR",
            source="database",
            message="Connection failed",
        ),
    ]

    result = analyze(events)

    assert result["total"] == 2
    assert result["cnt_level"]["INFO"] == 1
    assert result["cnt_level"]["ERROR"] == 1
    assert result["cnt_source"]["auth"] == 1
    assert result["cnt_source"]["database"] == 1


def test_analyze_empty() -> None:
    """Проверка анализа пустой последовательности событий"""

    result = analyze([])

    assert result["total"] == 0
    assert result["cnt_level"] == {}
    assert result["cnt_source"] == {}
    assert result["top_errors"] == []
    assert result["first_timestamp"] is None
    assert result["last_timestamp"] is None
