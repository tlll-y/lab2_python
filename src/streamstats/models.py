from dataclasses import dataclass
from datetime import datetime

from streamstats.constants import ALLOWED_LEVELS
from streamstats.errors import InvalidEventError, InvalidTimestampError


@dataclass
class Event:
    """Хранение информации об одном событии """

    timestamp: str
    level: str
    source: str
    message: str

    def __post_init__(self) -> None:
        """Проверяет правильность данных после создания объекта"""
        if self.level not in ALLOWED_LEVELS:
            raise InvalidEventError("Недопустимый уровень события")
        if not isinstance(self.source, str) or not self.source:
            raise InvalidEventError("Источник должен быть непустой строкой")
        if not isinstance(self.message, str):
            raise InvalidEventError("Сообщение должно быть строкой")
        if not isinstance(self.timestamp, str):
            raise InvalidTimestampError("Временная метка должна быть строкой")
        try:
            datetime.fromisoformat(self.timestamp)
        except ValueError as error:
            raise InvalidTimestampError("Неправильная временная метка") from error


@dataclass
class ParseStatistic:
    """Хранит количество пропущенных строк"""

    skip_lines: int = 0
