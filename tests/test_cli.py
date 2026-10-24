import json
import subprocess
import sys
from pathlib import Path


def test_cli_success(tmp_path: Path) -> None:
    """Проверка успешного запуска программы"""

    input_file = tmp_path / "events.jsonl"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        '{"timestamp":"2026-10-22T10:00:00Z",'
        '"level":"INFO","source":"auth","message":"User logged in"}\n',
        encoding="utf-8",
    )

    command = [
        sys.executable,
        "-m",
        "streamstats",
        "analyze",
        str(input_file),
        "--format",
        "jsonl",
        "--output",
        str(output_file),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert output_file.exists()

    report = json.loads(output_file.read_text(encoding="utf-8"))

    assert report["total"] == 1
    assert report["cnt_level"]["INFO"] == 1
    assert report["skipped_lines"] == 0


def test_cli_invalid_event(tmp_path: Path) -> None:
    """Проверяка кода завершения при ошибке в событии"""

    input_file = tmp_path / "invalid.jsonl"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        '{"timestamp":"2026-10-22T10:00:00Z",'
        '"level":"UNKNOWN","source":"auth","message":"Wrong"}\n',
        encoding="utf-8",
    )

    command = [
        sys.executable,
        "-m",
        "streamstats",
        "analyze",
        str(input_file),
        "--format",
        "jsonl",
        "--output",
        str(output_file),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert not output_file.exists()
    assert result.stdout == ""
    assert "Недопустимый уровень" in result.stderr
