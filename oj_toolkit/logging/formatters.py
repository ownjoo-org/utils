"""Log formatters for ownjoo-org projects.

Provides:
- HumanFormatter: timestamped, human-readable (local dev)
- ColoredHumanFormatter: same as HumanFormatter with level names colorized by severity
- JsonFormatter: structured JSON lines (deployed environments)
"""

import copy
import json
import logging
from datetime import datetime, timezone

from oj_toolkit.console.colors import Color
from oj_toolkit.logging.consts import LOG_FORMAT
from oj_toolkit.parsing.consts import TimeFormats

_LEVEL_COLORS: dict[str, str] = {
    'DEBUG':    Color.DIM,
    'INFO':     Color.CYAN,
    'WARNING':  Color.YELLOW,
    'ERROR':    Color.RED,
    'CRITICAL': Color.BOLD + Color.RED,
}


class HumanFormatter(logging.Formatter):
    """Human-readable formatter for local development."""

    def __init__(self):
        super().__init__(fmt=LOG_FORMAT, datefmt=TimeFormats.DATE_AND_TIME.value)


class ColoredHumanFormatter(HumanFormatter):
    """Human-readable formatter with level names colorized by severity.

    Uses the same format as HumanFormatter but wraps the levelname in ANSI
    color codes before rendering. The record is copied so the original is
    never mutated.

    Level colors:
        DEBUG    → dim
        INFO     → cyan
        WARNING  → yellow
        ERROR    → red
        CRITICAL → bold red
    """

    def format(self, record: logging.LogRecord) -> str:
        color = _LEVEL_COLORS.get(record.levelname)
        if color:
            record = copy.copy(record)
            record.levelname = Color.colorize(record.levelname, color)
        return super().format(record)


class JsonFormatter(logging.Formatter):
    """Structured JSON formatter for deployed environments.

    Emits one JSON object per log record. Extra fields (service, env) are
    injected into every record so logs from multiple services can be
    distinguished in a centralized destination.

    Designed to be subclassed — override `extra_fields` to inject
    additional context (e.g. aws_request_id, correlation_id).
    """

    def __init__(self, service: str, env: str):
        super().__init__()
        self.service = service
        self.env = env

    def extra_fields(self, record: logging.LogRecord) -> dict:  # pylint: disable=unused-argument
        """Override to inject additional fields into every log record."""
        return {}

    def format(self, record: logging.LogRecord) -> str:
        log_dict = {
            'timestamp': datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'service': self.service,
            'env': self.env,
            'message': record.getMessage(),
            **self.extra_fields(record),
        }
        if record.exc_info:
            log_dict['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_dict)
