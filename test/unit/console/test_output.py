"""Tests for console output utilities."""

import io
import unittest

from ownjoo_toolkit.console import Color, Output


class TestOutput(unittest.TestCase):
    """Tests for the Output class."""

    def test_should_write_to_stdout(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("Hello", "World")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "Hello World\n")

    def test_should_write_to_stderr(self):
        # setup
        stderr_capture = io.StringIO()
        output = Output(stderr=stderr_capture)

        # execute
        output.err("Error", "Message")

        # assess
        self.assertEqual(stderr_capture.getvalue(), "Error Message\n")

    def test_should_use_custom_separator(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("a", "b", "c", sep=";")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "a;b;c\n")

    def test_should_use_custom_end(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("message", end=" - done\n")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "message - done\n")

    def test_should_write_multiple_values(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("Status:", 200, "OK")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "Status: 200 OK\n")

    def test_should_convert_non_string_to_string(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("Count:", 42, "Items:", 3.14)

        # assess
        self.assertEqual(stdout_capture.getvalue(), "Count: 42 Items: 3.14\n")

    def test_should_write_empty_string_to_stdout(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "\n")

    def test_should_write_empty_string_to_stderr(self):
        # setup
        stderr_capture = io.StringIO()
        output = Output(stderr=stderr_capture)

        # execute
        output.err("")

        # assess
        self.assertEqual(stderr_capture.getvalue(), "\n")

    def test_should_separate_stdout_and_stderr(self):
        # setup
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        output = Output(stdout=stdout_capture, stderr=stderr_capture)

        # execute
        output.out("to stdout")
        output.err("to stderr")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "to stdout\n")
        self.assertEqual(stderr_capture.getvalue(), "to stderr\n")

    def test_should_write_without_newline(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("no newline", end="")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "no newline")

    def test_should_write_multiple_lines(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out("line1")
        output.out("line2")
        output.out("line3")

        # assess
        self.assertEqual(stdout_capture.getvalue(), "line1\nline2\nline3\n")

    def test_err_should_respect_custom_separator(self):
        # setup
        stderr_capture = io.StringIO()
        output = Output(stderr=stderr_capture)

        # execute
        output.err("code", "message", "details", sep="|")

        # assess
        self.assertEqual(stderr_capture.getvalue(), "code|message|details\n")

    def test_should_write_colored_text_to_stdout(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out_colored("Error", color=Color.RED)

        # assess
        result = stdout_capture.getvalue()
        self.assertIn(Color.RED, result)
        self.assertIn("Error", result)
        self.assertIn(Color.RESET, result)

    def test_should_write_colored_text_to_stderr(self):
        # setup
        stderr_capture = io.StringIO()
        output = Output(stderr=stderr_capture)

        # execute
        output.err_colored("Error", color=Color.RED)

        # assess
        result = stderr_capture.getvalue()
        self.assertIn(Color.RED, result)
        self.assertIn("Error", result)
        self.assertIn(Color.RESET, result)

    def test_should_combine_colors(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out_colored("Bold Red", color=Color.BOLD + Color.RED)

        # assess
        result = stdout_capture.getvalue()
        self.assertIn(Color.BOLD, result)
        self.assertIn(Color.RED, result)
        self.assertIn("Bold Red", result)

    def test_should_write_colored_multiple_values(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out_colored("Status", "OK", color=Color.GREEN)

        # assess
        result = stdout_capture.getvalue()
        self.assertIn(Color.GREEN, result)
        self.assertIn("Status OK", result)
        self.assertIn(Color.RESET, result)

    def test_should_write_red_text_shorthand(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out_red("Error")

        # assess
        result = stdout_capture.getvalue()
        self.assertIn(Color.RED, result)
        self.assertIn("Error", result)

    def test_should_write_green_text_shorthand(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out_green("Success")

        # assess
        result = stdout_capture.getvalue()
        self.assertIn(Color.GREEN, result)
        self.assertIn("Success", result)

    def test_should_write_yellow_text_shorthand(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out_yellow("Warning")

        # assess
        result = stdout_capture.getvalue()
        self.assertIn(Color.YELLOW, result)
        self.assertIn("Warning", result)

    def test_should_write_blue_text_shorthand(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out_blue("Info")

        # assess
        result = stdout_capture.getvalue()
        self.assertIn(Color.BLUE, result)
        self.assertIn("Info", result)

    def test_should_write_colored_text_to_stderr_shorthand(self):
        # setup
        stderr_capture = io.StringIO()
        output = Output(stderr=stderr_capture)

        # execute
        output.err_red("Error")

        # assess
        result = stderr_capture.getvalue()
        self.assertIn(Color.RED, result)
        self.assertIn("Error", result)

    def test_should_write_no_color_when_empty_color_code(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.out_colored("Plain text", color="")

        # assess
        result = stdout_capture.getvalue()
        self.assertEqual(result, "Plain text\n")

    def test_color_colorize_static_method(self):
        # setup
        text = "test"

        # execute
        colored = Color.colorize(text, Color.RED)

        # assess
        self.assertIn(Color.RED, colored)
        self.assertIn(text, colored)
        self.assertIn(Color.RESET, colored)

    def test_color_colorize_without_reset(self):
        # setup
        text = "test"

        # execute
        colored = Color.colorize(text, Color.RED, reset=False)

        # assess
        self.assertIn(Color.RED, colored)
        self.assertIn(text, colored)
        self.assertNotIn(Color.RESET, colored)

    def test_color_colorize_empty_color(self):
        # setup
        text = "plain"

        # execute
        colored = Color.colorize(text, color="")

        # assess
        self.assertEqual(colored, text)


if __name__ == "__main__":
    unittest.main()
