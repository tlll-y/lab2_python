from pathlib import Path

import pytest

from streamstats.errors import InvalidEventError
from streamstats.models import ParseStatistic
from streamstats.parsers import parse_csv, parse_jsonl


def test_parse_jsonl(tmp_path: Path) -> None:
    """Проверка чтения правильного JSONL"""

    filepath = tmp_path / "events.jsonl"

    filepath.write_text(
        '{"timestamp":"2026-10-22T10:00:00Z",'
        '"level":"INFO",'
        '"source":"auth",'
        '"message":"Hello"}\n',
        encoding="utf-8",
    )

    events = list(parse_jsonl(str(filepath)))

    assert len(events) == 1
    assert events[0].level == "INFO"
    assert events[0].source == "auth"


def test_parse_jsonl_skip_invalid(tmp_path: Path) -> None:
    """Проверка пропуска неправильной строки JSONL"""

    filepath = tmp_path / "invalid.jsonl"

    filepath.write_text(
        '{"timestamp":"2026-10-22T10:00:00Z","level":"INFO","source":"auth","message":"OK"}\n'
        '{"timestamp":"2026-10-22T10:01:00Z","level":"UNKNOWN","source":"server","message":"Wrong"}\n'
        '{"timestamp":"2026-10-22T10:02:00Z","level":"ERROR","source":"database","message":"Failed"}\n',
        encoding="utf-8",
    )

    stats = ParseStatistic()

    events = list(
        parse_jsonl(
            str(filepath),
            skip_invalid=True,
            stats=stats,
        )
    )

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[1].level == "ERROR"
    assert stats.skip_lines == 1


def test_parse_jsonl_without_skip(tmp_path: Path) -> None:
    """Проверка остановки при неправильной строке"""

    filepath = tmp_path / "invalid.jsonl"

    filepath.write_text(
        '{"timestamp":"2026-10-22T10:00:00Z","level":"UNKNOWN",'
        '"source":"auth","message":"Wrong"}\n',
        encoding="utf-8",
    )

    with pytest.raises(InvalidEventError):
        list(parse_jsonl(str(filepath)))


def test_parse_csv(tmp_path: Path) -> None:
    """Проверка чтения правильного CSV"""

    filepath = tmp_path / "events.csv"

    filepath.write_text(
        "timestamp,level,source,message\n"
        "2026-10-22T10:00:00Z,INFO,auth,Hello\n"
        "2026-10-22T10:05:00Z,ERROR,database,Failed\n",
        encoding="utf-8",
    )

    events = list(parse_csv(str(filepath)))

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[1].level == "ERROR"
    assert events[1].source == "database"
    assert events[0].message == "Hello"


def test_parse_csv_skip_invalid(tmp_path: Path) -> None:
    """Проверка пропуска неправильной записи CSV"""

    filepath = tmp_path / "invalid.csv"

    filepath.write_text(
        "timestamp,level,source,message\n"
        "2026-10-22T10:00:00Z,INFO,auth,OK\n"
        "2026-10-22T10:01:00Z,UNKNOWN,server,Wrong\n"
        "2026-10-22T10:02:00Z,ERROR,database,Failed\n",
        encoding="utf-8",
    )

    stats = ParseStatistic()

    events = list(
        parse_csv(
            str(filepath),
            skip_invalid=True,
            stats=stats,
        )
    )

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[1].level == "ERROR"
    assert stats.skip_lines == 1


def test_parse_csv_without_skip(tmp_path: Path) -> None:
    """Проверка остановку на неправильной записи CSV"""

    filepath = tmp_path / "invalid.csv"

    filepath.write_text(
        "timestamp,level,source,message\n"
        "2026-10-22T10:00:00Z,UNKNOWN,auth,Wrong\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidEventError):
        list(parse_csv(str(filepath)))


def test_parse_csv_empty_file(tmp_path: Path) -> None:
    """Проверка CSV-файл без заголовка(полностью пустого)"""

    filepath = tmp_path / "empty.csv"
    filepath.write_text("", encoding="utf-8")

    with pytest.raises(InvalidEventError):
        list(parse_csv(str(filepath)))


def test_parse_csv_header_only(tmp_path: Path) -> None:
    """Проверка CSV с заголовком, но без событий"""

    filepath = tmp_path / "header_only.csv"

    filepath.write_text(
        "timestamp,level,source,message\n",
        encoding="utf-8",
    )

    events = list(parse_csv(str(filepath)))

    assert events == []


def test_parse_jsonl_unicode(tmp_path: Path) -> None:
    """Проверка чтения русских букв в JSONL"""

    filepath = tmp_path / "unicode.jsonl"

    filepath.write_text(
        '{"timestamp":"2026-10-22T10:00:00Z",'
        '"level":"INFO",'
        '"source":"сервер",'
        '"message":"Пользователь вошёл в систему"}\n',
        encoding="utf-8",
    )

    events = list(parse_jsonl(str(filepath)))

    assert len(events) == 1
    assert events[0].source == "сервер"
    assert events[0].message == "Пользователь вошёл в систему"


def test_parse_csv_unicode(tmp_path: Path) -> None:
    """Проверка чтения русских букв в CSV"""

    filepath = tmp_path / "unicode.csv"

    filepath.write_text(
        "timestamp,level,source,message\n"
        "2026-10-22T10:00:00Z,INFO,сервер,Пользователь вошёл в систему\n",
        encoding="utf-8",
    )

    events = list(parse_csv(str(filepath)))

    assert len(events) == 1
    assert events[0].source == "сервер"
    assert events[0].message == "Пользователь вошёл в систему"


def test_parse_csv_broken_quotes(tmp_path: Path) -> None:
    """Проверка ошибку при незакрытой кавычке CSV"""

    filepath = tmp_path / "broken.csv"

    filepath.write_text(
        "timestamp,level,source,message\n"
        '2026-10-22T10:00:00Z,INFO,auth,"Unclosed\n',
        encoding="utf-8",
    )

    with pytest.raises(InvalidEventError):
        list(parse_csv(str(filepath)))
