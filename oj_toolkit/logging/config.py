"""Standardized logging configuration for ownjoo-org projects.

Usage (at application entry point — Lambda handler, CLI main, FastAPI lifespan):

    from oj_toolkit.logging import configure_logging

    configure_logging(service="my-service")                  # local dev defaults
    configure_logging(service="my-service", env="prod")      # JSON output
    configure_logging(service="my-service", level="DEBUG")    # explicit level as str
    configure_logging(service="my-service", level=logging.DEBUG)  # or int constant

Libraries should never call this — only application entry points.
"""

import logging
import os
import sys

from oj_toolkit.console.terminal import detect_color_support
from oj_toolkit.logging.consts import NOISY_LOGGERS
from oj_toolkit.logging.formatters import ColoredHumanFormatter, HumanFormatter, JsonFormatter

_DEFAULT_LEVEL = 'WARNING'


def configure_logging(
        service: str,
        env: str = 'local',
        level: int | str | None = None,
) -> None:
    """Configure the root logger for a project.

    Idempotent — does nothing if the root logger already has handlers.
    Call once at application startup.

    Args:
        service: Name of this service/project (appears in every log record).
        env: Runtime environment. 'local' produces human-readable output;
            any other value (e.g. 'dev', 'staging', 'prod') produces JSON lines.
        level: Log level as an int constant (e.g. logging.INFO) or name string
            ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
            Falls back to LOG_LEVEL env var, then logging.WARNING.
    """
    if isinstance(level, int):
        numeric_level = level
    else:
        resolved_level = level or os.environ.get('LOG_LEVEL', _DEFAULT_LEVEL)
        numeric_level = logging.getLevelName(resolved_level.upper())
        if not isinstance(numeric_level, int):
            numeric_level = logging.WARNING

    logging.root.setLevel(numeric_level)

    if logging.root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    if env == 'local':
        formatter = ColoredHumanFormatter() if detect_color_support() else HumanFormatter()
        handler.setFormatter(formatter)
    else:
        handler.setFormatter(JsonFormatter(service=service, env=env))

    logging.root.addHandler(handler)

    for name in NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
