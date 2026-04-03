"""Terminal and console output utilities.

Provides simple, efficient classes for writing to standard output and error streams,
with support for colored output using ANSI escape codes, and plans for formatting,
tables, and other terminal UI features.
"""

from ownjoo_utils.console.colors import Color
from ownjoo_utils.console.streams import Output

__all__ = ["Output", "Color"]
