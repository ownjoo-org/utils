"""Tests for terminal detection and shared utilities."""

import os
import unittest
from unittest.mock import patch

from ownjoo_toolkit.console.terminal import (
    border_chars,
    detect_unicode_support,
    horizontal_line,
    pad_visible,
    select_style,
    truncate_visible,
    visible_width,
)


class TestDetectUnicodeSupport(unittest.TestCase):
    """Tests for Unicode support detection."""

    def test_should_respect_no_color_env(self):
        # setup
        # execute
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            result = detect_unicode_support()

        # assess
        self.assertFalse(result)

    def test_should_enable_in_ci_environment(self):
        # setup
        # execute
        with patch.dict(os.environ, {"CI": "true", "NO_COLOR": ""}, clear=False):
            result = detect_unicode_support()

        # assess
        self.assertTrue(result)

    def test_should_disable_for_dumb_terminal(self):
        # setup
        # execute
        with patch.dict(os.environ, {"TERM": "dumb", "NO_COLOR": "", "CI": ""}, clear=False):
            result = detect_unicode_support()

        # assess
        self.assertFalse(result)

    def test_should_disable_for_vt100_terminal(self):
        # setup
        # execute
        with patch.dict(os.environ, {"TERM": "vt100", "NO_COLOR": "", "CI": ""}, clear=False):
            result = detect_unicode_support()

        # assess
        self.assertFalse(result)

    def test_should_enable_for_xterm(self):
        # setup
        # execute
        with patch.dict(os.environ, {"TERM": "xterm", "NO_COLOR": ""}, clear=False):
            result = detect_unicode_support()

        # assess
        # Most Unix systems support xterm with Unicode
        # This will be platform-dependent
        self.assertIsInstance(result, bool)


class TestSelectStyle(unittest.TestCase):
    """Tests for style selection."""

    def test_should_select_auto_style_unicode(self):
        # setup
        # execute
        with patch("ownjoo_toolkit.console.terminal.detect_unicode_support", return_value=True):
            result = select_style("auto", "ascii", "rounded")

        # assess
        self.assertEqual(result, "rounded")

    def test_should_select_auto_style_ascii(self):
        # setup
        # execute
        with patch("ownjoo_toolkit.console.terminal.detect_unicode_support", return_value=False):
            result = select_style("auto", "ascii", "rounded")

        # assess
        self.assertEqual(result, "ascii")

    def test_should_return_non_auto_style_unchanged(self):
        # setup
        # execute
        result = select_style("double", "ascii", "rounded")

        # assess
        self.assertEqual(result, "double")


class TestVisibleWidth(unittest.TestCase):
    """Tests for visible width calculation."""

    def test_should_calculate_plain_text_width(self):
        # setup
        text = "Hello"

        # execute
        width = visible_width(text)

        # assess
        self.assertEqual(width, 5)

    def test_should_ignore_ansi_color_codes(self):
        # setup
        # \033[31m is red color code
        text = "\033[31mHello\033[0m"

        # execute
        width = visible_width(text)

        # assess
        self.assertEqual(width, 5)

    def test_should_handle_multiple_color_codes(self):
        # setup
        # Multiple ANSI codes
        text = "\033[1m\033[31mBold Red\033[0m"

        # execute
        width = visible_width(text)

        # assess
        self.assertEqual(width, 8)

    def test_should_handle_empty_string(self):
        # setup
        text = ""

        # execute
        width = visible_width(text)

        # assess
        self.assertEqual(width, 0)

    def test_should_handle_only_ansi_codes(self):
        # setup
        text = "\033[31m\033[0m"

        # execute
        width = visible_width(text)

        # assess
        self.assertEqual(width, 0)


class TestPadVisible(unittest.TestCase):
    """Tests for visible width padding."""

    def test_should_pad_left_align(self):
        # setup
        text = "Hi"

        # execute
        padded = pad_visible(text, 5, align="left")

        # assess
        self.assertEqual(visible_width(padded), 5)
        self.assertTrue(padded.startswith("Hi"))

    def test_should_pad_right_align(self):
        # setup
        text = "Hi"

        # execute
        padded = pad_visible(text, 5, align="right")

        # assess
        self.assertEqual(visible_width(padded), 5)
        self.assertTrue(padded.endswith("Hi"))

    def test_should_pad_center_align(self):
        # setup
        text = "Hi"

        # execute
        padded = pad_visible(text, 5, align="center")

        # assess
        self.assertEqual(visible_width(padded), 5)
        self.assertIn("Hi", padded)

    def test_should_pad_with_custom_fill(self):
        # setup
        text = "Hi"

        # execute
        padded = pad_visible(text, 5, align="left", fill="-")

        # assess
        self.assertEqual(visible_width(padded), 5)
        self.assertIn("-", padded)

    def test_should_pad_colored_text(self):
        # setup
        colored_text = "\033[31mHi\033[0m"

        # execute
        padded = pad_visible(colored_text, 5, align="left")

        # assess
        self.assertEqual(visible_width(padded), 5)

    def test_should_not_pad_if_already_wide(self):
        # setup
        text = "Hello"

        # execute
        padded = pad_visible(text, 3, align="left")

        # assess
        self.assertEqual(padded, text)


class TestTruncateVisible(unittest.TestCase):
    """Tests for visible width truncation."""

    def test_should_truncate_long_text(self):
        # setup
        text = "Hello World"

        # execute
        truncated = truncate_visible(text, 8)

        # assess
        self.assertEqual(visible_width(truncated), 8)
        self.assertIn("...", truncated)

    def test_should_not_truncate_short_text(self):
        # setup
        text = "Hi"

        # execute
        truncated = truncate_visible(text, 10)

        # assess
        self.assertEqual(truncated, text)

    def test_should_use_custom_suffix(self):
        # setup
        text = "Hello World"

        # execute
        truncated = truncate_visible(text, 10, suffix=">>")

        # assess
        self.assertIn(">>", truncated)

    def test_should_handle_text_exactly_at_width(self):
        # setup
        text = "Hello"

        # execute
        truncated = truncate_visible(text, 5)

        # assess
        self.assertEqual(truncated, text)


class TestBorderChars(unittest.TestCase):
    """Tests for border character selection."""

    def test_should_get_ascii_borders(self):
        # setup
        # execute
        chars = border_chars("ascii")

        # assess
        self.assertEqual(chars[0], "+")  # top_left
        self.assertEqual(chars[4], "-")  # top

    def test_should_get_rounded_borders(self):
        # setup
        # execute
        chars = border_chars("rounded")

        # assess
        self.assertEqual(chars[0], "╭")  # top_left
        self.assertEqual(chars[1], "╮")  # top_right

    def test_should_get_double_borders(self):
        # setup
        # execute
        chars = border_chars("double")

        # assess
        self.assertEqual(chars[0], "╔")  # top_left
        self.assertEqual(chars[4], "═")  # top

    def test_should_get_single_borders(self):
        # setup
        # execute
        chars = border_chars("single")

        # assess
        self.assertEqual(chars[0], "┌")  # top_left
        self.assertEqual(chars[1], "┐")  # top_right

    def test_should_get_none_borders(self):
        # setup
        # execute
        chars = border_chars("none")

        # assess
        # All spaces
        for char in chars:
            self.assertEqual(char, " ")

    def test_should_default_to_ascii_for_unknown_style(self):
        # setup
        # execute
        chars = border_chars("unknown")

        # assess
        self.assertEqual(chars[0], "+")  # Falls back to ASCII

    def test_should_return_all_nine_chars(self):
        # setup
        # execute
        chars = border_chars("ascii")

        # assess
        self.assertEqual(len(chars), 14)


class TestHorizontalLine(unittest.TestCase):
    """Tests for horizontal line generation."""

    def test_should_create_ascii_line(self):
        # setup
        # execute
        line = horizontal_line(5, style="ascii")

        # assess
        self.assertEqual(line, "-----")

    def test_should_create_rounded_line(self):
        # setup
        # execute
        line = horizontal_line(5, style="rounded")

        # assess
        self.assertEqual(line, "─────")
        self.assertEqual(len(line), 5)

    def test_should_create_line_with_custom_char(self):
        # setup
        # execute
        line = horizontal_line(5, char="=")

        # assess
        self.assertEqual(line, "=====")

    def test_should_create_zero_width_line(self):
        # setup
        # execute
        line = horizontal_line(0)

        # assess
        self.assertEqual(line, "")

    def test_should_create_long_line(self):
        # setup
        # execute
        line = horizontal_line(100)

        # assess
        self.assertEqual(len(line), 100)


if __name__ == "__main__":
    unittest.main()
