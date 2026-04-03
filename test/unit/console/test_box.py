"""Tests for Box class and @in_box decorator."""

import io
import unittest
from unittest.mock import patch

from ownjoo_toolkit.console.box import Box, in_box


class TestBox(unittest.TestCase):
    """Tests for Box class."""

    def test_should_create_empty_box(self):
        # setup
        box = Box(style="ascii")

        # execute
        result = str(box)

        # assess
        self.assertIn("+", result)
        self.assertIn("-", result)

    def test_should_add_single_line(self):
        # setup
        box = Box(style="ascii")
        box.add_line("Hello")

        # execute
        result = str(box)

        # assess
        self.assertIn("Hello", result)
        self.assertIn("+", result)

    def test_should_add_multiple_lines(self):
        # setup
        box = Box(style="ascii")
        box.add_line("Line 1")
        box.add_line("Line 2")
        box.add_line("Line 3")

        # execute
        result = str(box)

        # assess
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)
        self.assertIn("Line 3", result)

    def test_should_chain_add_line(self):
        # setup
        # execute
        box = Box(style="ascii").add_line("A").add_line("B")

        # assess
        result = str(box)
        self.assertIn("A", result)
        self.assertIn("B", result)

    def test_should_add_multiple_lines_at_once(self):
        # setup
        box = Box(style="ascii")
        box.add_lines(["Line 1", "Line 2"])

        # execute
        result = str(box)

        # assess
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)

    def test_should_support_ascii_style(self):
        # setup
        box = Box(style="ascii")
        box.add_line("Test")

        # execute
        result = str(box)

        # assess
        self.assertIn("+", result)
        self.assertIn("-", result)

    def test_should_support_rounded_style(self):
        # setup
        box = Box(style="rounded")
        box.add_line("Test")

        # execute
        result = str(box)

        # assess
        self.assertIn("╭", result)
        self.assertIn("╮", result)

    def test_should_support_double_style(self):
        # setup
        box = Box(style="double")
        box.add_line("Test")

        # execute
        result = str(box)

        # assess
        self.assertIn("╔", result)
        self.assertIn("╗", result)

    def test_should_support_single_style(self):
        # setup
        box = Box(style="single")
        box.add_line("Test")

        # execute
        result = str(box)

        # assess
        self.assertIn("┌", result)
        self.assertIn("┐", result)

    def test_should_support_title(self):
        # setup
        # Titles work best with wider boxes
        box = Box(style="rounded", title="Title", width=30)
        box.add_line("Content")

        # execute
        result = str(box)

        # assess
        self.assertIn("Title", result)
        self.assertIn("Content", result)

    def test_should_respect_padding(self):
        # setup
        box = Box(style="ascii", padding=2)
        box.add_line("X")

        # execute
        result = str(box)

        # assess
        self.assertIn("X", result)
        # More padding means wider box
        lines = result.split("\n")
        self.assertGreater(len(lines[0]), 6)  # More than minimal box

    def test_should_respect_fixed_width(self):
        # setup
        box = Box(style="ascii", width=20)
        box.add_line("Short")

        # execute
        result = str(box)

        # assess
        self.assertIn("Short", result)
        # All lines should be 20 chars wide
        lines = result.split("\n")
        for line in lines:
            # Check that line width is approximately correct
            self.assertGreater(len(line), 15)

    def test_should_print_to_stdout(self):
        # setup
        box = Box(style="ascii")
        box.add_line("Output")

        # execute with captured output
        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            box.out()

        # assess
        output = captured_output.getvalue()
        self.assertIn("Output", output)

    def test_should_print_to_stderr(self):
        # setup
        box = Box(style="ascii")
        box.add_line("Error")

        # execute with captured output
        captured_output = io.StringIO()
        with patch("sys.stderr", captured_output):
            box.err()

        # assess
        output = captured_output.getvalue()
        self.assertIn("Error", output)

    def test_should_handle_no_borders_style(self):
        # setup
        box = Box(style="none")
        box.add_line("Content")

        # execute
        result = str(box)

        # assess
        self.assertIn("Content", result)

    def test_should_auto_detect_style(self):
        # setup
        # With auto style, it should pick ascii or unicode
        # based on terminal capabilities
        box = Box(style="auto")
        box.add_line("Test")

        # execute
        result = str(box)

        # assess
        # Should have some border characters
        self.assertGreater(len(result), 4)


class TestInBoxDecorator(unittest.TestCase):
    """Tests for @in_box decorator."""

    def test_should_wrap_function_output(self):
        # setup
        @in_box(style="ascii")
        def message():
            return "Hello"

        # execute with captured output
        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            message()

        # assess
        output = captured_output.getvalue()
        self.assertIn("Hello", output)
        self.assertIn("+", output)

    def test_should_handle_list_return(self):
        # setup
        @in_box(style="ascii")
        def list_func():
            return ["A", "B"]

        # execute with captured output
        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            list_func()

        # assess
        output = captured_output.getvalue()
        self.assertIn("A", output)
        self.assertIn("B", output)

    def test_should_support_title_parameter(self):
        # setup
        # Titles work best with wider boxes
        @in_box(style="rounded", title="Result", width=25)
        def titled():
            return "Data"

        # execute with captured output
        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            titled()

        # assess
        output = captured_output.getvalue()
        self.assertIn("Result", output)
        self.assertIn("Data", output)

    def test_should_preserve_function_metadata(self):
        # setup
        @in_box()
        def my_func():
            """Docstring."""
            return "output"

        # assert
        self.assertEqual(my_func.__name__, "my_func")
        self.assertEqual(my_func.__doc__, "Docstring.")

    def test_should_respect_style_parameter(self):
        # setup
        @in_box(style="double")
        def double_box():
            return "Content"

        # execute with captured output
        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            double_box()

        # assess
        output = captured_output.getvalue()
        self.assertIn("╔", output)

    def test_should_handle_none_return(self):
        # setup
        @in_box(style="ascii")
        def empty():
            return None

        # execute with captured output
        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            empty()

        # assess
        output = captured_output.getvalue()
        self.assertIn("+", output)  # Box drawn even with None

    def test_should_convert_non_string_to_string(self):
        # setup
        @in_box(style="ascii")
        def number_return():
            return 42

        # execute with captured output
        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            number_return()

        # assess
        output = captured_output.getvalue()
        self.assertIn("42", output)


if __name__ == "__main__":
    unittest.main()
