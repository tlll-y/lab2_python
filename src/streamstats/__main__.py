"""Запуск программы через командную строку"""

import argparse
import logging
from collections.abc import Iterator
from pathlib import Path

from streamstats.analysis import analyze
from streamstats.errors import StreamStatsError
from streamstats.models import Event, ParseStatistic
from streamstats.parsers import parse_csv, parse_jsonl
from streamstats.report import csv_report, json_report

logger = logging.getLogger(__name__)


def read_events(
        filepaths: list[str | Path],
        parse_function,
        skip_invalid: bool,
        stats: ParseStatistic,
) -> Iterator[Event]:
    """Последовательно читает события из нескольких файлов"""

    for filepath in filepaths:
        yield from parse_function(
            filepath,
            skip_invalid=skip_invalid,
            stats=stats,
        )


def main() -> int:
    """Обрабатывает аргументы запуска и выполняет анализ"""
    parser = argparse.ArgumentParser(
        description="Потоковый анализатор CSV и JSONL"
    )
    parser.add_argument("command", choices=["analyze"])
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument(
        "--format",
        choices=["csv", "jsonl"],
        required=True,
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )
    parser.add_argument("--skip-invalid", action="store_true")
    parser.add_argument(
        "--report-format",
        choices=["json", "csv"],
        default="json",
    )
    args = parser.parse_args()
    stats = ParseStatistic()

    if args.format == "csv":
        parse_function = parse_csv
    else:
        parse_function = parse_jsonl

    events = read_events(
        args.inputs,
        parse_function,
        args.skip_invalid,
        stats,
    )

    try:
        result = analyze(events)
        result["skipped_lines"] = stats.skip_lines

        if args.report_format == "csv":
            csv_report(result, args.output)
        else:
            json_report(result, args.output)

    except (StreamStatsError, OSError) as error:
        logger.error("%s", error)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
