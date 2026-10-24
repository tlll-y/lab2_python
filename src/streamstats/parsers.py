import csv
import json
import logging
from collections.abc import Iterator
from pathlib import Path

from streamstats.constants import REQUIRED_FIELDS
from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.models import Event, ParseStatistic

logger = logging.getLogger(__name__)


def parse_jsonl(
        filepath: str | Path,
        skip_invalid: bool = False,
        stats: ParseStatistic | None = None,
) -> Iterator[Event]:
    """
    Читает события из JSONL-файла

    :param filepath: Путь к файлу
    :param skip_invalid: Пропускать/не пропускать неправильные строки
    :param stats: Объект для подсчёта пропущенных строк
    :return: Итератор объектов Event
    """
    if stats is None:
        stats = ParseStatistic()

    with open(filepath, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                data = json.loads(line)

                if not isinstance(data, dict):
                    raise InvalidEventError("Ожидался JSON-объект")

                event = Event(
                    timestamp=data["timestamp"],
                    level=data["level"],
                    source=data["source"],
                    message=data["message"],
                )

            except (
                    json.JSONDecodeError,
                    KeyError,
                    TypeError,
                    InvalidEventError,
                    InvalidTimestampError,
            ) as error:
                message = f"Файл {filepath}, строка {line_number}: {error}"

                if skip_invalid:
                    stats.skip_lines += 1
                    logger.warning("%s", message)
                    continue

                raise InvalidEventError(message) from error

            yield event


def parse_csv(
        filepath: str | Path,
        skip_invalid: bool = False,
        stats: ParseStatistic | None = None,
) -> Iterator[Event]:
    """
    Читает события из CSV-файла


    :param filepath: Путь к CSV-файлу
    :param skip_invalid: Пропускать/не пропускать неправильные строки
    :param stats: Объект для подсчёта пропущенных строк
    :return: Итератор объектов Event
    """
    if stats is None:
        stats = ParseStatistic()

    with open(filepath, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, strict=True)
        if reader.fieldnames is None:
            raise InvalidEventError(f"Файл {filepath}: отсутствует заголовок CSV")
        missing_fields = REQUIRED_FIELDS - set(reader.fieldnames)

        if missing_fields:
            raise InvalidEventError(
                f"Файл {filepath}: отсутствуют столбцы {missing_fields}"
            )

        while True:
            try:
                data = next(reader)
            except StopIteration:
                break
            except csv.Error as error:
                raise InvalidEventError(
                    f"Файл {filepath}, строка {reader.line_num}: ошибка CSV: {error}"
                ) from error

            try:
                if None in data:
                    raise InvalidEventError("В CSV-записи превышено количество значений")
                event = Event(
                    timestamp=data["timestamp"],
                    level=data["level"],
                    source=data["source"],
                    message=data["message"],
                )
            except(
                    KeyError,
                    TypeError,
                    InvalidEventError,
                    InvalidTimestampError,
            ) as error:

                message = (
                    f"Файл {filepath}, строка {reader.line_num}: {error}"
                )
                if skip_invalid:
                    stats.skip_lines += 1
                    logger.warning("%s", message)
                    continue
                raise InvalidEventError(message) from error

            yield event
