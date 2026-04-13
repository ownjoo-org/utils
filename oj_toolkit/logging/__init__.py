"""Standardized logging for ownjoo-org projects.

Configure once at application startup:

    from oj_toolkit.logging import configure_logging
    configure_logging(service="my-service")           # local: human-readable
    configure_logging(service="my-service", env="prod")  # deployed: JSON lines

Generator decorators:

    from oj_toolkit.logging import timed_generator, timed_async_generator
"""

from oj_toolkit.logging.config import configure_logging
from oj_toolkit.logging.consts import LOG_FORMAT
from oj_toolkit.logging.decorators import timed_generator, timed_async_generator
from oj_toolkit.logging.formatters import ColoredHumanFormatter, HumanFormatter, JsonFormatter

__all__ = [
    'configure_logging',
    'LOG_FORMAT',
    'timed_generator',
    'timed_async_generator',
    'ColoredHumanFormatter',
    'HumanFormatter',
    'JsonFormatter',
]
