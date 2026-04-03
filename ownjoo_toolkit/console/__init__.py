"""Terminal and console output utilities.

Provides simple, efficient classes for writing to standard output and error streams,
with support for colored output using ANSI escape codes, chainable colored text builders,
and formatting utilities for tables, boxes, and status displays.
"""

from ownjoo_toolkit.console.box import Box, in_box
from ownjoo_toolkit.console.colored_text import ColoredText
from ownjoo_toolkit.console.colors import Color
from ownjoo_toolkit.console.status import (
    progress_bar,
    status_badge,
    status_line,
    status_wrapped,
)
from ownjoo_toolkit.console.streams import Output
from ownjoo_toolkit.console.table import Table, tabulated

__all__ = [
    "Output",
    "Color",
    "ColoredText",
    "Table",
    "tabulated",
    "Box",
    "in_box",
    "status_line",
    "progress_bar",
    "status_badge",
    "status_wrapped",
]
