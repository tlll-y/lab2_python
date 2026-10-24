from collections import Counter
from collections.abc import Iterable
from datetime import UTC, datetime

from streamstats.models import Event


def analyze(events: Iterable[Event]) -> dict:
    """Собирает общую статистику по событиям"""

    total = 0
    cnt_level: Counter[str] = Counter()
    cnt_source: Counter[str] = Counter()
    error_counts: Counter[tuple[str, str]] = Counter()

    first_timestamp = None
    last_timestamp = None
    for event in events:
        total += 1

        cnt_level[event.level] += 1
        cnt_source[event.source] += 1

        if event.level in ("ERROR", "CRITICAL"):
            key = (event.source, event.level)
            error_counts[key] += 1
        current_time = datetime.fromisoformat(event.timestamp)

        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=UTC)

        if first_timestamp is None or current_time < first_timestamp:
            first_timestamp = current_time
        if last_timestamp is None or current_time > last_timestamp:
            last_timestamp = current_time

    top_errors = sorted(
        error_counts.items(),
        key=lambda item: (
            -item[1],
            0 if item[0][1] == "CRITICAL" else 1,
            item[0][0],
        )
    )[:5]

    top_five = []

    for (source, level), count in top_errors:
        top_five.append({
            "source": source,
            "level": level,
            "count": count,
        })

    return {
        "total": total,
        "cnt_level": dict(cnt_level),
        "cnt_source": dict(cnt_source),
        "first_timestamp": (
            first_timestamp.isoformat()
            if first_timestamp is not None
            else None
        ),
        "last_timestamp": (
            last_timestamp.isoformat()
            if last_timestamp is not None
            else None
        ),
        "top_errors": top_five,
    }
