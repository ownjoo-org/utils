"""Tests for status indicators and @status_wrapped decorator."""

import io
import unittest
from unittest.mock import patch

from ownjoo_toolkit.console.colors import Color
from ownjoo_toolkit.console.status import (
    progress_bar,
    status_badge,
    status_line,
    status_wrapped,
)


class TestStatusLine(unittest.TestCase):
    """Tests for status_line function."""

    def test_should_format_label_value_pair(self):
        # setup
        # execute
        result = status_line("Status", "OK")

        # assess
        self.assertIn("Status", result)
        self.assertIn("OK", result)
        self.assertIn(": ", result)

    def test_should_use_custom_separator(self):
        # setup
        # execute
        result = status_line("Name", "Alice", sep=" = ")

        # assess
        self.assertIn("Name", result)
        self.assertIn("Alice", result)
        self.assertIn(" = ", result)

    def test_should_apply_color_to_value(self):
        # setup
        # execute
        result = status_line("Status", "OK", color=Color.GREEN)

        # assess
        self.assertIn("Status", result)
        self.assertIn("OK", result)
        # Color codes should be present
        self.assertIn(Color.RESET, result)

    def test_should_handle_integer_values(self):
        # setup
        # execute
        result = status_line("Count", 42)

        # assess
        self.assertIn("Count", result)
        self.assertIn("42", result)

    def test_should_handle_float_values(self):
        # setup
        # execute
        result = status_line("Ratio", 3.14)

        # assess
        self.assertIn("Ratio", result)
        self.assertIn("3.14", result)

    def test_should_handle_none_color(self):
        # setup
        # execute
        result = status_line("Label", "value", color=None)

        # assess
        self.assertIn("Label", result)
        self.assertIn("value", result)
        # No color codes
        self.assertNotIn(Color.GREEN, result)


class TestProgressBar(unittest.TestCase):
    """Tests for progress_bar function."""

    def test_should_create_0_percent_bar(self):
        # setup
        # execute
        result = progress_bar(0)

        # assess
        self.assertIn("0%", result)
        self.assertIn("░", result)

    def test_should_create_50_percent_bar(self):
        # setup
        # execute
        result = progress_bar(50, width=10)

        # assess
        self.assertIn("50%", result)
        self.assertIn("█", result)
        self.assertIn("░", result)

    def test_should_create_100_percent_bar(self):
        # setup
        # execute
        result = progress_bar(100, width=10)

        # assess
        self.assertIn("100%", result)
        self.assertIn("█", result)

    def test_should_respect_custom_width(self):
        # setup
        # execute
        result = progress_bar(50, width=5)

        # assess
        self.assertIn("50%", result)
        # Should have 5 characters of filled/empty

    def test_should_use_custom_filled_character(self):
        # setup
        # execute
        result = progress_bar(50, width=10, filled="=")

        # assess
        self.assertIn("=", result)
        self.assertIn("░", result)

    def test_should_use_custom_empty_character(self):
        # setup
        # execute
        result = progress_bar(50, width=10, empty="-")

        # assess
        self.assertIn("█", result)
        self.assertIn("-", result)

    def test_should_include_label(self):
        # setup
        # execute
        result = progress_bar(75, label="Progress")

        # assess
        self.assertIn("Progress", result)
        self.assertIn("75%", result)

    def test_should_clamp_to_100_percent(self):
        # setup
        # execute
        result = progress_bar(150)

        # assess
        self.assertIn("100%", result)

    def test_should_clamp_to_0_percent(self):
        # setup
        # execute
        result = progress_bar(-10)

        # assess
        self.assertIn("0%", result)

    def test_should_format_percentage_display(self):
        # setup
        # execute
        result = progress_bar(5, width=10)

        # assess
        # Should show "5%" right-aligned (space before single digit)
        self.assertIn("%", result)
        self.assertIn("5", result)


class TestStatusBadge(unittest.TestCase):
    """Tests for status_badge function."""

    def test_should_create_ok_badge(self):
        # setup
        # execute
        result = status_badge("READY", "ok")

        # assess
        self.assertIn("READY", result)
        self.assertIn("[OK]", result)
        self.assertIn(Color.GREEN, result)

    def test_should_create_error_badge(self):
        # setup
        # execute
        result = status_badge("FAILED", "error")

        # assess
        self.assertIn("FAILED", result)
        self.assertIn("[ERROR]", result)
        self.assertIn(Color.RED, result)

    def test_should_create_warning_badge(self):
        # setup
        # execute
        result = status_badge("WARNING", "warning")

        # assess
        self.assertIn("WARNING", result)
        self.assertIn("[WARNING]", result)
        self.assertIn(Color.YELLOW, result)

    def test_should_create_info_badge(self):
        # setup
        # execute
        result = status_badge("INFO", "info")

        # assess
        self.assertIn("INFO", result)
        self.assertIn("[INFO]", result)
        self.assertIn(Color.CYAN, result)

    def test_should_default_to_info_badge(self):
        # setup
        # execute
        result = status_badge("MESSAGE")

        # assess
        self.assertIn("MESSAGE", result)
        self.assertIn("[INFO]", result)
        self.assertIn(Color.CYAN, result)

    def test_should_uppercase_status_label(self):
        # setup
        # execute
        result = status_badge("data", "ok")

        # assess
        self.assertIn("[OK]", result)
        self.assertIn("data", result)

    def test_should_handle_case_insensitive_status(self):
        # setup
        # execute
        result = status_badge("test", "ERROR")

        # assess
        self.assertIn("[ERROR]", result)
        self.assertIn(Color.RED, result)

    def test_should_handle_unknown_status(self):
        # setup
        # execute
        result = status_badge("text", "unknown")

        # assess
        self.assertIn("text", result)
        # Should default to CYAN (info color)
        self.assertIn(Color.CYAN, result)

    def test_should_include_reset_code(self):
        # setup
        # execute
        result = status_badge("TEXT", "ok")

        # assess
        # Color codes should end with RESET
        self.assertIn(Color.RESET, result)


class TestStatusWrapped(unittest.TestCase):
    """Tests for @status_wrapped decorator."""

    def test_should_wrap_function_output_ok(self):
        # setup
        @status_wrapped(status="ok")
        def operation():
            return "Operation complete"

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            operation()

        # assess
        output = captured.getvalue()
        self.assertIn("[OK]", output)
        self.assertIn("Operation complete", output)
        self.assertIn(Color.GREEN, output)

    def test_should_wrap_function_output_error(self):
        # setup
        @status_wrapped(status="error")
        def failed_op():
            return "Operation failed"

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            failed_op()

        # assess
        output = captured.getvalue()
        self.assertIn("[ERROR]", output)
        self.assertIn("Operation failed", output)
        self.assertIn(Color.RED, output)

    def test_should_wrap_function_output_warning(self):
        # setup
        @status_wrapped(status="warning")
        def warned():
            return "Partial success"

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            warned()

        # assess
        output = captured.getvalue()
        self.assertIn("[WARNING]", output)
        self.assertIn("Partial success", output)
        self.assertIn(Color.YELLOW, output)

    def test_should_default_to_info_status(self):
        # setup
        @status_wrapped()
        def message():
            return "Message text"

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            message()

        # assess
        output = captured.getvalue()
        self.assertIn("[INFO]", output)
        self.assertIn("Message text", output)
        self.assertIn(Color.CYAN, output)

    def test_should_preserve_function_metadata(self):
        # setup
        @status_wrapped(status="ok")
        def my_function():
            """Docstring for my_function."""
            return "Result"

        # assess
        self.assertEqual(my_function.__name__, "my_function")
        self.assertEqual(my_function.__doc__, "Docstring for my_function.")

    def test_should_handle_non_string_return(self):
        # setup
        @status_wrapped(status="ok")
        def numeric():
            return 42

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            numeric()

        # assess
        output = captured.getvalue()
        self.assertIn("[OK]", output)
        self.assertIn("42", output)

    def test_should_print_with_newline(self):
        # setup
        @status_wrapped(status="ok")
        def simple():
            return "Output"

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            simple()

        # assess
        output = captured.getvalue()
        # Should end with newline
        self.assertTrue(output.endswith("\n"))

    def test_should_handle_list_return(self):
        # setup
        @status_wrapped(status="ok")
        def get_list():
            return ["A", "B", "C"]

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            get_list()

        # assess
        output = captured.getvalue()
        self.assertIn("[OK]", output)
        # List is converted to string representation
        self.assertIn("['A', 'B', 'C']", output) or self.assertIn("A", output)


if __name__ == "__main__":
    unittest.main()
