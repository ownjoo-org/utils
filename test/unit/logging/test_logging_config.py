"""Tests for configure_logging, HumanFormatter, ColoredHumanFormatter, and JsonFormatter."""

import json
import logging
import sys
import unittest
from io import StringIO
from unittest.mock import patch

from oj_toolkit.logging.config import configure_logging
from oj_toolkit.logging.formatters import ColoredHumanFormatter, HumanFormatter, JsonFormatter


def _reset_root_logger():
    """Remove all handlers from the root logger so configure_logging can re-run."""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.root.setLevel(logging.WARNING)


class TestHumanFormatter(unittest.TestCase):
    """Tests for HumanFormatter."""

    def test_formats_record(self):
        formatter = HumanFormatter()
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='hello world', args=(), exc_info=None,
        )
        output = formatter.format(record)
        self.assertIn('hello world', output)
        self.assertIn('INFO', output)
        self.assertIn('test', output)


class TestColoredHumanFormatter(unittest.TestCase):
    """Tests for ColoredHumanFormatter."""

    def _make_record(self, level=logging.INFO, msg='test message'):
        return logging.LogRecord(
            name='test', level=level, pathname='', lineno=0,
            msg=msg, args=(), exc_info=None,
        )

    def test_contains_ansi_codes_for_info(self):
        formatter = ColoredHumanFormatter()
        output = formatter.format(self._make_record(logging.INFO))
        self.assertIn('\033[', output)

    def test_contains_ansi_codes_for_warning(self):
        formatter = ColoredHumanFormatter()
        output = formatter.format(self._make_record(logging.WARNING))
        self.assertIn('\033[', output)

    def test_contains_ansi_codes_for_error(self):
        formatter = ColoredHumanFormatter()
        output = formatter.format(self._make_record(logging.ERROR))
        self.assertIn('\033[', output)

    def test_contains_ansi_codes_for_critical(self):
        formatter = ColoredHumanFormatter()
        output = formatter.format(self._make_record(logging.CRITICAL))
        self.assertIn('\033[', output)

    def test_does_not_mutate_original_record(self):
        formatter = ColoredHumanFormatter()
        record = self._make_record(logging.WARNING)
        original_levelname = record.levelname
        formatter.format(record)
        self.assertEqual(record.levelname, original_levelname)

    def test_message_still_present(self):
        formatter = ColoredHumanFormatter()
        output = formatter.format(self._make_record(msg='important message'))
        self.assertIn('important message', output)


class TestJsonFormatter(unittest.TestCase):
    """Tests for JsonFormatter."""

    def setUp(self):
        self.formatter = JsonFormatter(service='test-svc', env='prod')

    def test_valid_json(self):
        record = logging.LogRecord(
            name='mymodule', level=logging.WARNING, pathname='', lineno=0,
            msg='something happened', args=(), exc_info=None,
        )
        output = self.formatter.format(record)
        data = json.loads(output)
        self.assertEqual(data['service'], 'test-svc')
        self.assertEqual(data['env'], 'prod')
        self.assertEqual(data['level'], 'WARNING')
        self.assertEqual(data['logger'], 'mymodule')
        self.assertEqual(data['message'], 'something happened')
        self.assertIn('timestamp', data)

    def test_exception_included(self):
        exc_info = None
        try:
            raise ValueError('boom')
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name='test', level=logging.ERROR, pathname='', lineno=0,
            msg='error', args=(), exc_info=exc_info,
        )
        output = self.formatter.format(record)
        data = json.loads(output)
        self.assertIn('exception', data)
        self.assertIn('ValueError', data['exception'])

    def test_extra_fields_override(self):
        """Subclassing JsonFormatter and overriding extra_fields injects custom fields."""
        class CustomFormatter(JsonFormatter):
            """Formatter that injects a static request_id."""
            def extra_fields(self, record):
                return {'request_id': 'abc-123'}

        formatter = CustomFormatter(service='svc', env='staging')
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='msg', args=(), exc_info=None,
        )
        data = json.loads(formatter.format(record))
        self.assertEqual(data['request_id'], 'abc-123')


class TestConfigureLogging(unittest.TestCase):
    """Tests for configure_logging."""

    def setUp(self):
        _reset_root_logger()

    def tearDown(self):
        _reset_root_logger()

    def test_installs_handler(self):
        configure_logging(service='svc')
        self.assertEqual(len(logging.root.handlers), 1)

    def test_local_uses_human_formatter_when_not_tty(self):
        with patch('oj_toolkit.console.terminal.sys.stdout') as mock_stdout:
            mock_stdout.isatty.return_value = False
            configure_logging(service='svc', env='local')
        self.assertIsInstance(logging.root.handlers[0].formatter, HumanFormatter)
        self.assertNotIsInstance(logging.root.handlers[0].formatter, ColoredHumanFormatter)

    def test_local_uses_colored_formatter_when_tty(self):
        with patch('oj_toolkit.console.terminal.sys.stdout') as mock_stdout:
            mock_stdout.isatty.return_value = True
            with patch.dict('os.environ', {'NO_COLOR': '', 'TERM': 'xterm-256color'}, clear=False):
                configure_logging(service='svc', env='local')
        self.assertIsInstance(logging.root.handlers[0].formatter, ColoredHumanFormatter)

    def test_non_local_uses_json_formatter(self):
        configure_logging(service='svc', env='prod')
        self.assertIsInstance(logging.root.handlers[0].formatter, JsonFormatter)

    def test_level_int(self):
        configure_logging(service='svc', level=logging.DEBUG)
        self.assertEqual(logging.root.level, logging.DEBUG)

    def test_level_str(self):
        configure_logging(service='svc', level='INFO')
        self.assertEqual(logging.root.level, logging.INFO)

    def test_level_from_env_var(self):
        with patch.dict('os.environ', {'LOG_LEVEL': 'DEBUG'}):
            configure_logging(service='svc')
        self.assertEqual(logging.root.level, logging.DEBUG)

    def test_level_defaults_to_warning(self):
        configure_logging(service='svc')
        self.assertEqual(logging.root.level, logging.WARNING)

    def test_idempotent(self):
        configure_logging(service='svc')
        configure_logging(service='svc')
        configure_logging(service='svc', env='prod')
        self.assertEqual(len(logging.root.handlers), 1)

    def test_noisy_loggers_set_to_warning(self):
        configure_logging(service='svc', level='DEBUG')
        for name in ('urllib3', 'boto3', 'botocore', 's3transfer', 'requests'):
            self.assertEqual(logging.getLogger(name).level, logging.WARNING,
                             f'{name} should be WARNING')

    def test_writes_to_stdout(self):
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(HumanFormatter())
        logging.root.addHandler(handler)
        logging.root.setLevel(logging.INFO)

        logging.getLogger('test.write').info('visible message')
        self.assertIn('visible message', stream.getvalue())

    def test_json_output_parseable(self):
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter(service='svc', env='prod'))
        logging.root.addHandler(handler)
        logging.root.setLevel(logging.INFO)

        logging.getLogger('test.json').info('structured log')
        line = stream.getvalue().strip()
        data = json.loads(line)
        self.assertEqual(data['message'], 'structured log')
        self.assertEqual(data['service'], 'svc')


if __name__ == '__main__':
    unittest.main()
