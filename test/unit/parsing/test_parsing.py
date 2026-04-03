import unittest
from datetime import datetime
from typing import Optional

from ownjoo_utils.parsing.consts import TimeFormats
from ownjoo_utils.parsing.types import get_datetime, get_value, str_to_list, validate


class TestParsingFunctions(unittest.TestCase):
    def test_should_get_validated_type(self):
        # setup
        expected: str = 'blah'

        # execute
        actual = validate(v=expected, exp=str, default='')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_default_type(self):
        # setup
        expected: str = ''

        # execute
        actual = validate(v=[], exp=str, default=expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_list_from_str(self):
        # setup
        expected: list = ['a', 'b', 'c']
        sep: str = ';'

        # execute
        actual = str_to_list(
            v=sep.join(expected),
            separator=sep,
        )

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_list_from_str(self):
        # setup
        expected: list = ['a', 'b', 'c']
        abc: str = ','.join(expected)

        # execute
        actual = validate(v=abc, exp=list)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_dict(self):
        # setup
        expected: dict = {0: 'a', 1: 'b', 2: 'c'}

        # execute
        actual = validate(v=expected, exp=dict)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_default_dict(self):
        # setup
        expected: dict = {}

        # execute
        actual = validate(v='not a dict', exp=dict, default={})

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_none(self):
        # setup
        expected: Optional[dict] = None

        # execute
        actual = validate(v='not a dict', exp=dict)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_with_validator(self):
        # setup
        expected: str = 'blah'

        # execute
        actual = validate(v=expected, exp=str, validator=lambda x, *args, **kwargs: x == expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_default_on_validation_fail(self):
        # setup
        expected: str = ''

        # execute
        actual = validate(v='blah', exp=str, validator=lambda x, *args, **kwargs: x is None, default=expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_validated_with_converter(self):
        # setup
        expected: str = 'blah'
        unwanted: str = '_more'

        # execute
        actual = validate(
            v=f'{expected}{unwanted}',
            exp=str,
            converter=lambda x, *args, **kwargs: x.removesuffix(unwanted),
            validator=lambda x, *args, **kwargs: x == expected,
        )

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_time_formats(self):
        # setup

        # execute/assess
        for format_str in TimeFormats:
            self.assertIsNotNone(format_str)
            self.assertIsNotNone(format_str.value)

        # teardown

    def test_should_get_datetime_from_str(self):
        # setup
        expected: str = 'Sun, 06 Nov 1994 08:49:37 GMT'

        # execute
        actual: datetime = get_datetime(v=expected, exp=datetime)

        # assess
        self.assertIsInstance(actual, datetime)

        # teardown

    def test_should_get_datetime_from_float(self):
        # setup
        expected: float = datetime.now().timestamp()

        # execute
        actual: datetime = get_datetime(v=expected, exp=datetime)

        # assess
        self.assertIsInstance(expected, float)
        self.assertIsInstance(actual, datetime)

        # teardown

    def test_should_get_value_from_list(self):
        # setup
        expected: str = 'blah'

        # execute
        actual = get_value(src=['', [expected]], path=[1, 0], exp=str, default='')

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_value_from_dict(self):
        # setup
        expected: str = 'blah'

        # execute
        actual = get_value(src={'first': 'a', 'second': [expected]}, path=['second', 0], exp=str)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_value_with_passed_validator(self):
        # setup
        expected: str = 'blah'

        # execute
        actual = get_value(src=expected, exp=str, validator=lambda x, *args, **kwargs: x == expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_return_none_on_str_to_list_with_empty_separator(self):
        # setup
        value: str = 'a,b,c'

        # execute
        actual = str_to_list(v=value, separator='')

        # assess
        self.assertEqual(value, actual)

        # teardown

    def test_should_return_unchanged_on_str_to_list_with_non_string(self):
        # setup
        expected: int = 123

        # execute
        actual = str_to_list(v=expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_handle_get_value_with_invalid_path(self):
        # setup
        src: dict = {'a': {'b': 'c'}}
        expected: Optional[dict] = None

        # execute
        actual = get_value(src=src, path=['x', 'y', 'z'])

        # assess
        # When path navigation fails, post_processor (validate) is called on src
        # validate returns None when src doesn't match expected type
        self.assertIsNone(actual)

        # teardown

    def test_should_validate_none_value_with_default(self):
        # setup
        expected: str = 'default'

        # execute
        actual = validate(v=None, exp=str, default=expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_datetime_with_none_value(self):
        # setup
        expected: Optional[datetime] = None

        # execute
        actual = get_datetime(v=None)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    def test_should_get_datetime_from_datetime_object(self):
        # setup
        expected: datetime = datetime(2024, 1, 15, 10, 30, 0)

        # execute
        actual = get_datetime(v=expected)

        # assess
        self.assertEqual(expected, actual)

        # teardown

    # Happy path: str_to_list with various separators
    def test_should_split_with_custom_separator(self):
        # setup
        expected: list = ['hello', 'world', 'test']
        value: str = 'hello|world|test'

        # execute
        actual = str_to_list(v=value, separator='|')

        # assess
        self.assertEqual(expected, actual)

    def test_should_split_single_item(self):
        # setup
        expected: list = ['single']
        value: str = 'single'

        # execute
        actual = str_to_list(v=value)

        # assess
        self.assertEqual(expected, actual)

    def test_should_split_with_spaces(self):
        # setup
        expected: list = ['item1', 'item2', 'item3']
        value: str = 'item1 item2 item3'

        # execute
        actual = str_to_list(v=value, separator=' ')

        # assess
        self.assertEqual(expected, actual)

    # Unhappy path: str_to_list when separator not found
    def test_should_return_list_with_whole_string_when_separator_not_found(self):
        # setup
        value: str = 'noseparatorhere'
        expected: list = ['noseparatorhere']

        # execute
        actual = str_to_list(v=value, separator='|')

        # assess
        self.assertEqual(expected, actual)

    def test_should_return_none_on_str_to_list_with_none_input(self):
        # setup
        # execute
        actual = str_to_list(v=None)

        # assess
        self.assertIsNone(actual)

    # Happy path: get_datetime with ISO 8601 format
    def test_should_get_datetime_from_iso_format(self):
        # setup
        expected_str: str = '2024-01-15T10:30:00'

        # execute
        actual = get_datetime(v=expected_str)

        # assess
        self.assertIsInstance(actual, datetime)
        self.assertEqual(actual.year, 2024)
        self.assertEqual(actual.month, 1)
        self.assertEqual(actual.day, 15)

    # Happy path: get_datetime with custom format
    def test_should_get_datetime_with_custom_format(self):
        # setup
        value: str = '15/01/2024 14:30'
        format_str: str = '%d/%m/%Y %H:%M'

        # execute
        actual = get_datetime(v=value, format_str=format_str)

        # assess
        self.assertIsInstance(actual, datetime)
        self.assertEqual(actual.day, 15)
        self.assertEqual(actual.month, 1)

    # Happy path: get_datetime with integer timestamp
    def test_should_get_datetime_from_integer_timestamp(self):
        # setup
        timestamp: int = 1234567890

        # execute
        actual = get_datetime(v=timestamp)

        # assess
        self.assertIsInstance(actual, datetime)
        self.assertEqual(actual.year, 2009)

    # Unhappy path: get_datetime with invalid string
    def test_should_return_none_on_get_datetime_with_invalid_string(self):
        # setup
        value: str = 'not a valid datetime'

        # execute
        actual = get_datetime(v=value)

        # assess
        self.assertIsNone(actual)

    # Unhappy path: get_datetime with invalid timestamp
    def test_should_return_none_on_get_datetime_with_invalid_timestamp(self):
        # setup
        value: float = 999999999999999999.999

        # execute
        actual = get_datetime(v=value)

        # assess
        self.assertIsNone(actual)

    # Happy path: validate with falsy values
    def test_should_validate_zero_as_integer(self):
        # setup
        value: int = 0

        # execute
        actual = validate(v=value, exp=int)

        # assess
        self.assertEqual(actual, 0)
        self.assertIsInstance(actual, int)

    def test_should_validate_empty_string(self):
        # setup
        value: str = ''

        # execute
        actual = validate(v=value, exp=str)

        # assess
        self.assertEqual(actual, '')
        self.assertIsInstance(actual, str)

    def test_should_validate_false_boolean(self):
        # setup
        value: bool = False

        # execute
        actual = validate(v=value, exp=bool)

        # assess
        self.assertEqual(actual, False)
        self.assertIsInstance(actual, bool)

    # Unhappy path: validate with converter that raises exception
    def test_should_return_default_when_converter_raises_exception(self):
        # setup
        def failing_converter(v, **kwargs):
            raise ValueError('Conversion failed')

        expected: str = 'default_value'

        # execute
        actual = validate(v='test', converter=failing_converter, exp=str, default=expected)

        # assess
        self.assertEqual(actual, expected)

    # Unhappy path: validate with validator that raises exception
    def test_should_return_default_when_validator_raises_exception(self):
        # setup
        def failing_validator(v, *args, **kwargs):
            raise ValueError('Validation failed')

        expected: str = 'default_value'

        # execute
        actual = validate(v='test', exp=str, validator=failing_validator, default=expected)

        # assess
        self.assertEqual(actual, expected)

    # Happy path: get_value with deeply nested structure
    def test_should_get_value_from_deeply_nested_dict(self):
        # setup
        expected: str = 'deep_value'
        src: dict = {
            'level1': {
                'level2': {
                    'level3': {
                        'target': expected
                    }
                }
            }
        }

        # execute
        actual = get_value(src=src, path=['level1', 'level2', 'level3', 'target'], exp=str)

        # assess
        self.assertEqual(actual, expected)

    def test_should_get_value_from_mixed_dict_list_structure(self):
        # setup
        expected: str = 'mixed_value'
        src: dict = {
            'items': [
                {'id': 1, 'data': 'wrong'},
                {'id': 2, 'data': [expected, 'other']},
            ]
        }

        # execute
        actual = get_value(src=src, path=['items', 1, 'data', 0], exp=str)

        # assess
        self.assertEqual(actual, expected)

    # Happy path: get_value with falsy extracted values
    def test_should_extract_zero_from_nested_structure(self):
        # setup
        src: dict = {'numbers': [1, 2, 0, 4]}

        # execute
        actual = get_value(src=src, path=['numbers', 2], exp=int)

        # assess
        self.assertEqual(actual, 0)

    def test_should_extract_empty_list_from_nested_structure(self):
        # setup
        src: dict = {'data': [[], 'other', 'items']}

        # execute
        actual = get_value(src=src, path=['data', 0], exp=list)

        # assess
        self.assertEqual(actual, [])

    # Unhappy path: get_value with missing intermediate key
    def test_should_return_default_on_missing_intermediate_key(self):
        # setup
        src: dict = {'a': {'b': 'value'}}
        expected: str = 'default'

        # execute
        actual = get_value(src=src, path=['x', 'y', 'z'], exp=str, default=expected)

        # assess
        self.assertEqual(actual, expected)

    # Unhappy path: get_value with mismatched index type
    def test_should_return_default_when_accessing_list_with_string_key(self):
        # setup
        src: dict = {'items': ['a', 'b', 'c']}
        expected: str = 'default'

        # execute
        actual = get_value(src=src, path=['items', 'invalid_index'], exp=str, default=expected)

        # assess
        self.assertEqual(actual, expected)

    # Happy path: get_value with no path (post-process source directly)
    def test_should_post_process_source_when_path_is_none(self):
        # setup
        value: str = 'test_string'

        # execute
        actual = get_value(src=value, path=None, exp=str)

        # assess
        self.assertEqual(actual, value)

    # Happy path: get_value with no post_processor
    def test_should_return_raw_value_when_no_post_processor(self):
        # setup
        expected: str = 'raw_value'
        src: dict = {'key': expected}

        # execute
        actual = get_value(src=src, path=['key'], post_processor=None)

        # assess
        self.assertEqual(actual, expected)

    # Edge case: validate with None as default (explicit)
    def test_should_allow_none_as_default_value(self):
        # setup
        # execute
        actual = validate(v=[], exp=str, default=None)

        # assess
        self.assertIsNone(actual)

    # Edge case: str_to_list with single character separator
    def test_should_split_with_single_char_separator(self):
        # setup
        expected: list = ['a', 'b', 'c']
        value: str = 'a,b,c'

        # execute
        actual = str_to_list(v=value, separator=',')

        # assess
        self.assertEqual(expected, actual)

    # Edge case: get_datetime with zero timestamp
    def test_should_get_datetime_from_zero_timestamp(self):
        # setup
        value: int = 0

        # execute
        actual = get_datetime(v=value)

        # assess
        self.assertIsInstance(actual, datetime)
        # 0 represents epoch time (1970-01-01)

    # Edge case: validate with no explicit default (should return None)
    def test_should_return_none_when_validation_fails_with_no_default(self):
        # setup
        # execute
        actual = validate(v=[], exp=str)

        # assess
        self.assertIsNone(actual)


if __name__ == '__main__':
    unittest.main()
