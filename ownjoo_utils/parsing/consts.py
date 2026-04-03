from enum import Enum
from typing import Callable

DEFAULT_CONVERTER: Callable = lambda value, *args, **kwargs: value
DEFAULT_VALIDATOR: Callable = lambda value, expected_type, *args, **kwargs: isinstance(value, expected_type)
DEFAULT_SEPARATOR: str = ','


class TimeFormats(Enum):
    date_and_time = '%Y/%m/%d %H:%M:%S'
    iso8601 = '%Y-%m-%dT%H:%M:%S'
    http = '%a, %d %b %Y %H:%M:%S GMT'
