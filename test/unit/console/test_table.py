"""Tests for Table class and @tabulated decorator."""

import io
import unittest
from unittest.mock import patch

from ownjoo_utils.console.table import Table, tabulated


class TestTable(unittest.TestCase):
    """Tests for Table class."""

    def test_should_create_empty_table(self):
        # setup
        table = Table(style="ascii")

        # execute
        result = str(table)

        # assess
        self.assertEqual(result, "")

    def test_should_add_simple_row(self):
        # setup
        table = Table(headers=["Name"], style="ascii")
        table.add_row("Alice")

        # execute
        result = str(table)

        # assess
        self.assertIn("Name", result)
        self.assertIn("Alice", result)
        self.assertIn("+", result)

    def test_should_add_multiple_rows(self):
        # setup
        table = Table(headers=["ID", "Status"], columns=2, style="ascii")
        table.add_row(1, "OK")
        table.add_row(2, "ERROR")

        # execute
        result = str(table)

        # assess
        self.assertIn("ID", result)
        self.assertIn("Status", result)
        self.assertIn("OK", result)
        self.assertIn("ERROR", result)

    def test_should_chain_add_row(self):
        # setup
        # execute
        table = (
            Table(headers=["A"], style="ascii")
            .add_row("1")
            .add_row("2")
            .add_row("3")
        )

        # assess
        result = str(table)
        self.assertIn("1", result)
        self.assertIn("2", result)
        self.assertIn("3", result)

    def test_should_auto_detect_dict_input(self):
        # setup
        table = Table(style="ascii")
        data = [
            {"name": "Alice", "status": "OK"},
            {"name": "Bob", "status": "FAIL"},
        ]

        # execute
        table.add_rows(data)
        result = str(table)

        # assess
        self.assertIn("name", result)
        self.assertIn("status", result)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)

    def test_should_auto_detect_tuple_input(self):
        # setup
        table = Table(style="ascii")
        data = [("Task 1", "OK"), ("Task 2", "ERROR")]

        # execute
        table.add_rows(data)
        result = str(table)

        # assess
        self.assertIn("Task 1", result)
        self.assertIn("OK", result)

    def test_should_auto_detect_key_value_pairs(self):
        # setup
        table = Table(style="ascii")
        data = [("host", "localhost"), ("port", "8080")]

        # execute
        table.add_rows(data)
        result = str(table)

        # assess
        self.assertIn("Key", result)
        self.assertIn("Value", result)
        self.assertIn("host", result)
        self.assertIn("localhost", result)

    def test_should_handle_string_list_input(self):
        # setup
        table = Table(style="ascii")
        data = ["Item 1", "Item 2", "Item 3"]

        # execute
        table.add_rows(data)
        result = str(table)

        # assess
        self.assertIn("Item 1", result)
        self.assertIn("Item 2", result)

    def test_should_support_ascii_style(self):
        # setup
        table = Table(headers=["A", "B"], style="ascii")
        table.add_row("1", "2")

        # execute
        result = str(table)

        # assess
        self.assertIn("+", result)
        self.assertIn("-", result)

    def test_should_support_rounded_style(self):
        # setup
        table = Table(headers=["A"], style="rounded")
        table.add_row("1")

        # execute
        result = str(table)

        # assess
        self.assertIn("╭", result)
        self.assertIn("╮", result)

    def test_should_support_double_style(self):
        # setup
        table = Table(headers=["A"], style="double")
        table.add_row("1")

        # execute
        result = str(table)

        # assess
        self.assertIn("╔", result)
        self.assertIn("╗", result)

    def test_should_support_single_style(self):
        # setup
        table = Table(headers=["A"], style="single")
        table.add_row("1")

        # execute
        result = str(table)

        # assess
        self.assertIn("┌", result)
        self.assertIn("┐", result)

    def test_should_set_column_width(self):
        # setup
        table = Table(headers=["Name"], style="ascii")
        table.set_column_width(0, 20)
        table.add_row("Alice")

        # execute
        result = str(table)

        # assess
        # First data line should be wider
        self.assertIn("Alice", result)
        lines = result.split("\n")
        self.assertGreater(len(lines[0]), 15)  # Border line is wider

    def test_should_set_column_alignment(self):
        # setup
        table = Table(headers=["Val"], columns=1, style="ascii")
        table.set_align(0, "right")
        table.add_row("5")

        # execute
        result = str(table)

        # assess
        self.assertIn("5", result)

    def test_should_respect_padding(self):
        # setup
        table = Table(headers=["X"], style="ascii", padding=3)
        table.add_row("Y")

        # execute
        result = str(table)

        # assess
        # More padding = wider box
        lines = result.split("\n")
        self.assertGreater(len(lines[0]), 7)  # At least border + padded content

    def test_should_auto_detect_columns(self):
        # setup
        table = Table(style="ascii")
        data = [
            {"a": "1", "b": "2", "c": "3"},
            {"a": "4", "b": "5", "c": "6"},
        ]

        # execute
        table.add_rows(data)
        result = str(table)

        # assess
        self.assertIn("a", result)
        self.assertIn("b", result)
        self.assertIn("c", result)

    def test_should_print_to_stdout(self):
        # setup
        table = Table(headers=["A"], style="ascii")
        table.add_row("1")

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            table.out()

        # assess
        output = captured.getvalue()
        self.assertIn("1", output)

    def test_should_print_to_stderr(self):
        # setup
        table = Table(headers=["A"], style="ascii")
        table.add_row("1")

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stderr", captured):
            table.err()

        # assess
        output = captured.getvalue()
        self.assertIn("1", output)

    def test_should_handle_empty_rows_list(self):
        # setup
        table = Table(style="ascii")
        table.add_rows([])

        # execute
        result = str(table)

        # assess
        self.assertEqual(result, "")

    def test_should_convert_values_to_strings(self):
        # setup
        table = Table(headers=["Num"], style="ascii")
        table.add_row(42)
        table.add_row(3.14)

        # execute
        result = str(table)

        # assess
        self.assertIn("42", result)
        self.assertIn("3.14", result)

    def test_should_handle_mixed_row_lengths(self):
        # setup
        table = Table(style="ascii", columns=3)
        table.add_row("A", "B")
        table.add_row("X", "Y", "Z")

        # execute
        result = str(table)

        # assess
        self.assertIn("A", result)
        self.assertIn("Z", result)


class TestTabulatedDecorator(unittest.TestCase):
    """Tests for @tabulated decorator."""

    def test_should_wrap_list_of_tuples(self):
        # setup
        @tabulated(headers=["ID", "Value"])
        def get_data():
            return [(1, "A"), (2, "B")]

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            get_data()

        # assess
        output = captured.getvalue()
        self.assertIn("ID", output)
        self.assertIn("Value", output)
        self.assertIn("1", output)
        self.assertIn("A", output)

    def test_should_auto_detect_dict_list(self):
        # setup
        @tabulated()
        def get_records():
            return [
                {"name": "Alice", "role": "Admin"},
                {"name": "Bob", "role": "User"},
            ]

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            get_records()

        # assess
        output = captured.getvalue()
        self.assertIn("name", output)
        self.assertIn("Alice", output)

    def test_should_handle_generator(self):
        # setup
        @tabulated(columns=2)
        def gen_data():
            yield ("A", "1")
            yield ("B", "2")

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            gen_data()

        # assess
        output = captured.getvalue()
        self.assertIn("A", output)
        self.assertIn("B", output)

    def test_should_respect_style_parameter(self):
        # setup
        @tabulated(headers=["X"], style="ascii")
        def data():
            return [("1",)]

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            data()

        # assess
        output = captured.getvalue()
        self.assertIn("+", output)  # ASCII style

    def test_should_preserve_function_name(self):
        # setup
        @tabulated()
        def my_table():
            return []

        # assert
        self.assertEqual(my_table.__name__, "my_table")

    def test_should_handle_empty_iterable(self):
        # setup
        @tabulated(headers=["A", "B"])
        def empty():
            return []

        # execute with captured output
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            empty()

        # assess
        output = captured.getvalue()
        # Should still print headers
        self.assertIn("A", output)


if __name__ == "__main__":
    unittest.main()
