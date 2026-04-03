"""Tests for ColoredText chainable builder."""

import io
import unittest

from ownjoo_toolkit.console import Color, ColoredText, Output


class TestColoredText(unittest.TestCase):
    """Tests for ColoredText class."""

    def test_should_create_empty_colored_text(self):
        # setup
        # execute
        text = ColoredText()

        # assess
        self.assertEqual(list(text), [])
        self.assertEqual(str(text), "")

    def test_should_add_single_segment(self):
        # setup
        # execute
        text = ColoredText().add("hello", Color.RED)

        # assess
        segments = list(text)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0], ("hello", Color.RED))

    def test_should_chain_red_method(self):
        # setup
        # execute
        text = ColoredText().red("error")

        # assess
        segments = list(text)
        self.assertEqual(segments[0], ("error", Color.RED))

    def test_should_chain_green_method(self):
        # setup
        # execute
        text = ColoredText().green("success")

        # assess
        segments = list(text)
        self.assertEqual(segments[0], ("success", Color.GREEN))

    def test_should_chain_yellow_method(self):
        # setup
        # execute
        text = ColoredText().yellow("warning")

        # assess
        segments = list(text)
        self.assertEqual(segments[0], ("warning", Color.YELLOW))

    def test_should_chain_blue_method(self):
        # setup
        # execute
        text = ColoredText().blue("info")

        # assess
        segments = list(text)
        self.assertEqual(segments[0], ("info", Color.BLUE))

    def test_should_chain_multiple_segments(self):
        # setup
        # execute
        text = (ColoredText()
            .red("ERROR: ")
            .white("something went wrong")
            .cyan(" (code: 500)")
        )

        # assess
        segments = list(text)
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[0][1], Color.RED)
        self.assertEqual(segments[1][1], Color.WHITE)
        self.assertEqual(segments[2][1], Color.CYAN)

    def test_should_render_ansi_string(self):
        # setup
        text = ColoredText().red("error")

        # execute
        result = str(text)

        # assess
        self.assertIn(Color.RED, result)
        self.assertIn("error", result)
        self.assertIn(Color.RESET, result)

    def test_should_render_multiple_segments_with_colors(self):
        # setup
        text = (ColoredText()
            .red("ERROR")
            .white(": ")
            .yellow("warning")
        )

        # execute
        result = str(text)

        # assess
        self.assertIn(Color.RED, result)
        self.assertIn(Color.WHITE, result)
        self.assertIn(Color.YELLOW, result)
        # Colors separate segments with RESET, so check for parts
        self.assertIn("ERROR", result)
        self.assertIn(": ", result)
        self.assertIn("warning", result)

    def test_should_consume_iterable_of_segments(self):
        # setup
        def gen():
            yield ("Status: ", Color.BOLD)
            yield ("OK", Color.GREEN)

        # execute
        text = ColoredText().from_iter(gen())

        # assess
        segments = list(text)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0], ("Status: ", Color.BOLD))
        self.assertEqual(segments[1], ("OK", Color.GREEN))

    def test_should_be_iterable(self):
        # setup
        text = (ColoredText()
            .red("a")
            .green("b")
            .blue("c")
        )

        # execute
        segments = list(text)

        # assess
        self.assertEqual(len(segments), 3)
        for _, (segment_text, color) in enumerate(text):
            self.assertIsNotNone(segment_text)
            self.assertIsNotNone(color)

    def test_should_print_to_stdout_with_out(self):
        # setup
        stdout_capture = io.StringIO()
        text = ColoredText(stdout=stdout_capture).red("error")

        # execute
        text.out()

        # assess
        result = stdout_capture.getvalue()
        self.assertIn(Color.RED, result)
        self.assertIn("error", result)
        self.assertIn("\n", result)

    def test_should_print_to_stderr_with_err(self):
        # setup
        stderr_capture = io.StringIO()
        text = ColoredText(stderr=stderr_capture).red("error")

        # execute
        text.err()

        # assess
        result = stderr_capture.getvalue()
        self.assertIn(Color.RED, result)
        self.assertIn("error", result)
        self.assertIn("\n", result)

    def test_should_support_bold_method(self):
        # setup
        # execute
        text = ColoredText().bold("important")

        # assess
        segments = list(text)
        self.assertEqual(segments[0], ("important", Color.BOLD))

    def test_should_support_dim_method(self):
        # setup
        # execute
        text = ColoredText().dim("subtle")

        # assess
        segments = list(text)
        self.assertEqual(segments[0], ("subtle", Color.DIM))

    def test_should_support_reset_method(self):
        # setup
        # execute
        text = ColoredText().reset("normal")

        # assess
        segments = list(text)
        self.assertEqual(segments[0], ("normal", Color.RESET))

    def test_should_convert_non_string_to_string(self):
        # setup
        # execute
        text = ColoredText().red("Code: ").green(404)

        # assess
        segments = list(text)
        self.assertEqual(segments[1][0], "404")

    def test_should_support_combined_colors(self):
        # setup
        combined = Color.BOLD + Color.RED

        # execute
        text = ColoredText().add("bold red", combined)

        # assess
        result = str(text)
        self.assertIn(Color.BOLD, result)
        self.assertIn(Color.RED, result)
        self.assertIn("bold red", result)

    def test_should_support_magenta_and_cyan_methods(self):
        # setup
        # execute
        magenta = ColoredText().magenta("magenta")
        cyan = ColoredText().cyan("cyan")

        # assess
        self.assertEqual(list(magenta)[0][1], Color.MAGENTA)
        self.assertEqual(list(cyan)[0][1], Color.CYAN)

    def test_should_support_white_method(self):
        # setup
        # execute
        text = ColoredText().white("white text")

        # assess
        segments = list(text)
        self.assertEqual(segments[0][1], Color.WHITE)

    def test_should_output_without_newline_on_request(self):
        # setup
        stdout_capture = io.StringIO()
        text = ColoredText(stdout=stdout_capture).red("no newline")

        # execute
        text.out(end="")

        # assess
        result = stdout_capture.getvalue()
        self.assertNotIn("\n", result)

    def test_should_add_without_color(self):
        # setup
        # execute
        text = ColoredText().add("plain text")

        # assess
        result = str(text)
        self.assertEqual(result, "plain text")


class TestColoredTextWithOutput(unittest.TestCase):
    """Tests for ColoredText integration with Output class."""

    def test_output_segment_should_return_colored_text(self):
        # setup
        output = Output()

        # execute
        segment = output.segment()

        # assess
        self.assertIsInstance(segment, ColoredText)

    def test_output_segment_should_chain_colors(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        output.segment().red("ERROR: ").white("failed").out()

        # assess
        result = stdout_capture.getvalue()
        self.assertIn(Color.RED, result)
        self.assertIn(Color.WHITE, result)
        # Colors separate segments, check parts
        self.assertIn("ERROR: ", result)
        self.assertIn("failed", result)

    def test_output_segment_for_stderr(self):
        # setup
        stderr_capture = io.StringIO()
        output = Output(stderr=stderr_capture)

        # execute
        output.segment().red("CRITICAL").cyan(": system error").err()

        # assess
        result = stderr_capture.getvalue()
        self.assertIn(Color.RED, result)
        self.assertIn(Color.CYAN, result)

    def test_output_segment_complex_chain(self):
        # setup
        stdout_capture = io.StringIO()
        output = Output(stdout=stdout_capture)

        # execute
        (output.segment()
            .bold("Status: ")
            .green("OK")
            .reset(" (")
            .cyan("2.5s")
            .reset(")")
            .out())

        # assess
        result = stdout_capture.getvalue()
        self.assertIn(Color.BOLD, result)
        self.assertIn(Color.GREEN, result)
        self.assertIn(Color.CYAN, result)
        # Check for parts separately due to color codes between segments
        self.assertIn("Status: ", result)
        self.assertIn("OK", result)
        self.assertIn("2.5s", result)

    def test_output_segment_inherits_streams(self):
        # setup
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        output = Output(stdout=stdout_capture, stderr=stderr_capture)

        # execute
        output.segment().green("success").out()
        output.segment().red("error").err()

        # assess
        stdout_result = stdout_capture.getvalue()
        stderr_result = stderr_capture.getvalue()
        self.assertIn("success", stdout_result)
        self.assertIn("error", stderr_result)


if __name__ == "__main__":
    unittest.main()
