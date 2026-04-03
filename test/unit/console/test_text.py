"""Tests for text formatting utilities and decorators."""

import io
import unittest
from unittest.mock import patch

from ownjoo_toolkit.console.text import (
    boxed,
    center,
    pad_left,
    pad_right,
    repeat,
    truncate,
)


class TestPadLeft(unittest.TestCase):
    """Tests for left padding."""

    def test_should_pad_left(self):
        # setup
        text = "Hi"

        # execute
        result = pad_left(text, 5)

        # assess
        self.assertIn("Hi", result)
        self.assertEqual(len(result), 5)

    def test_should_not_pad_if_already_wide(self):
        # setup
        text = "Hello"

        # execute
        result = pad_left(text, 3)

        # assess
        self.assertEqual(result, text)

    def test_should_pad_with_custom_fill(self):
        # setup
        text = "Hi"

        # execute
        result = pad_left(text, 5, fill=".")

        # assess
        self.assertIn("...", result)
        self.assertIn("Hi", result)


class TestPadRight(unittest.TestCase):
    """Tests for right padding."""

    def test_should_pad_right(self):
        # setup
        text = "Hi"

        # execute
        result = pad_right(text, 5)

        # assess
        self.assertEqual(len(result), 5)
        self.assertTrue(result.startswith("Hi"))

    def test_should_not_pad_if_already_wide(self):
        # setup
        text = "Hello"

        # execute
        result = pad_right(text, 3)

        # assess
        self.assertEqual(result, text)

    def test_should_pad_with_custom_fill(self):
        # setup
        text = "Hi"

        # execute
        result = pad_right(text, 5, fill="-")

        # assess
        self.assertIn("---", result)
        self.assertTrue(result.startswith("Hi"))


class TestCenter(unittest.TestCase):
    """Tests for centering."""

    def test_should_center_text(self):
        # setup
        text = "Hi"

        # execute
        result = center(text, 5)

        # assess
        self.assertEqual(len(result), 5)
        self.assertIn("Hi", result)

    def test_should_not_pad_if_already_wide(self):
        # setup
        text = "Hello"

        # execute
        result = center(text, 3)

        # assess
        self.assertEqual(result, text)

    def test_should_center_with_custom_fill(self):
        # setup
        text = "X"

        # execute
        result = center(text, 5, fill="-")

        # assess
        self.assertEqual(len(result), 5)
        self.assertIn("X", result)
        self.assertIn("-", result)


class TestTruncate(unittest.TestCase):
    """Tests for truncation."""

    def test_should_truncate_long_text(self):
        # setup
        text = "Hello World"

        # execute
        result = truncate(text, 8)

        # assess
        self.assertIn("...", result)
        self.assertLessEqual(len(result), 11)  # "Hello" + "..."

    def test_should_not_truncate_short_text(self):
        # setup
        text = "Hi"

        # execute
        result = truncate(text, 10)

        # assess
        self.assertEqual(result, text)

    def test_should_use_custom_suffix(self):
        # setup
        text = "Hello World"

        # execute
        result = truncate(text, 10, suffix=">>")

        # assess
        self.assertIn(">>", result)

    def test_should_truncate_exactly_at_width(self):
        # setup
        text = "Hello"

        # execute
        result = truncate(text, 5)

        # assess
        self.assertEqual(result, text)


class TestRepeat(unittest.TestCase):
    """Tests for text repetition."""

    def test_should_repeat_text(self):
        # setup
        text = "ab"

        # execute
        result = repeat(text, 3)

        # assess
        self.assertEqual(result, "ababab")

    def test_should_repeat_zero_times(self):
        # setup
        text = "a"

        # execute
        result = repeat(text, 0)

        # assess
        self.assertEqual(result, "")

    def test_should_repeat_once(self):
        # setup
        text = "hello"

        # execute
        result = repeat(text, 1)

        # assess
        self.assertEqual(result, text)

    def test_should_repeat_single_char(self):
        # setup
        # execute
        result = repeat("=", 5)

        # assess
        self.assertEqual(result, "=====")


class TestBoxedDecorator(unittest.TestCase):
    """Tests for @boxed decorator."""

    def test_should_wrap_string_return_value(self):
        # setup
        @boxed(style="ascii")
        def greeting():
            return "Hello"

        # execute with captured output
        import sys

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            greeting()

        # assess
        output = captured_output.getvalue()
        self.assertIn("Hello", output)
        self.assertIn("+", output)  # ASCII border

    def test_should_wrap_list_return_value(self):
        # setup
        @boxed(style="ascii")
        def items():
            return ["Item 1", "Item 2"]

        # execute with captured output
        import sys

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            items()

        # assess
        output = captured_output.getvalue()
        self.assertIn("Item 1", output)
        self.assertIn("Item 2", output)
        self.assertIn("+", output)

    def test_should_handle_none_return_value(self):
        # setup
        @boxed(style="ascii")
        def empty():
            return None

        # execute with captured output
        import sys

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            empty()

        # assess
        output = captured_output.getvalue()
        self.assertIn("+", output)  # Box is still drawn

    def test_should_respect_style_parameter(self):
        # setup
        @boxed(style="ascii")
        def message():
            return "Test"

        # execute with captured output
        import sys

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            message()

        # assess
        output = captured_output.getvalue()
        self.assertIn("+", output)  # ASCII style uses +

    def test_should_preserve_function_name(self):
        # setup
        @boxed()
        def my_function():
            return "output"

        # assess
        self.assertEqual(my_function.__name__, "my_function")

    def test_should_handle_tuple_return_value(self):
        # setup
        @boxed(style="ascii")
        def tuple_data():
            return ("Line 1", "Line 2")

        # execute with captured output
        import sys

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            tuple_data()

        # assess
        output = captured_output.getvalue()
        self.assertIn("Line 1", output)
        self.assertIn("Line 2", output)


if __name__ == "__main__":
    unittest.main()
