class StreamStatsError(Exception):
    """Общая ошибка программы"""


class InvalidEventError(StreamStatsError):
    """Ошибка в данных события"""


class InvalidTimestampError(StreamStatsError):
    """Неправильная дата или время события"""


class UnsupportedFormatError(StreamStatsError):
    """Неподдерживаемый формат файла"""


class CLIConfigError(StreamStatsError):
    """Ошибка конфигурации командной строки(CLI)"""
