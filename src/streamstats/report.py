import csv
import json
from pathlib import Path


def json_report(report: dict, filepath: str | Path) -> None:
    """Записывает отчёт в JSON-файл"""

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)


def csv_report(report: dict, filepath: str | Path) -> None:
    """Записывает отчёт в CSV-файл по разделам"""

    with open(filepath, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["Общая статистика"])
        for field in (
            "total",
            "skipped_lines",
            "first_timestamp",
            "last_timestamp",
        ):
            writer.writerow([field, report[field]])

        writer.writerow([])

        writer.writerow(["Количество по уровням"])
        writer.writerow(["level", "count"])
        for level, count in report["cnt_level"].items():
            writer.writerow([level, count])

        writer.writerow([])

        writer.writerow(["Количество по источникам"])
        writer.writerow(["source", "count"])
        for source, count in report["cnt_source"].items():
            writer.writerow([source, count])

        writer.writerow([])

        writer.writerow(["Топ ошибок"])
        writer.writerow(["source", "level", "count"])
        for error in report["top_errors"]:
            writer.writerow([
                error["source"],
                error["level"],
                error["count"],
            ])
