"""Tests for async_chunks function."""
from unittest import IsolatedAsyncioTestCase

from ownjoo_toolkit.asynchronous.async_chunks import a_chunks


async def async_range(n: int):
    """Helper to generate async iterable from range."""
    for i in range(n):
        yield i


async def async_list(items: list):
    """Helper to generate async iterable from list."""
    for item in items:
        yield item


class TestAsyncChunks(IsolatedAsyncioTestCase):
    """Tests for a_chunks function."""

    async def test_basic_chunking(self):
        """Test basic chunking with multiple complete chunks."""
        result = []
        async for chunk in a_chunks(3, async_range(9)):
            result.append(chunk)
        self.assertEqual(result, [[0, 1, 2], [3, 4, 5], [6, 7, 8]])

    async def test_partial_final_chunk(self):
        """Test that remaining items smaller than chunk_size are yielded."""
        result = []
        async for chunk in a_chunks(3, async_range(7)):
            result.append(chunk)
        self.assertEqual(result, [[0, 1, 2], [3, 4, 5], [6]])

    async def test_chunk_size_one(self):
        """Test chunking with size 1."""
        result = []
        async for chunk in a_chunks(1, async_range(3)):
            result.append(chunk)
        self.assertEqual(result, [[0], [1], [2]])

    async def test_chunk_size_larger_than_items(self):
        """Test chunk size larger than number of items."""
        result = []
        async for chunk in a_chunks(10, async_range(3)):
            result.append(chunk)
        self.assertEqual(result, [[0, 1, 2]])

    async def test_empty_async_iterable(self):
        """Test with empty async iterable."""
        result = []
        async for chunk in a_chunks(3, async_range(0)):
            result.append(chunk)
        self.assertEqual(result, [])

    async def test_single_item(self):
        """Test with single item."""
        result = []
        async for chunk in a_chunks(3, async_range(1)):
            result.append(chunk)
        self.assertEqual(result, [[0]])

    async def test_exact_multiple_of_chunk_size(self):
        """Test when items are exact multiple of chunk_size."""
        result = []
        async for chunk in a_chunks(5, async_range(15)):
            result.append(chunk)
        self.assertEqual(
            result,
            [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14]],
        )

    async def test_with_string_items(self):
        """Test chunking with non-numeric items."""
        result = []
        items = ["a", "b", "c", "d", "e"]
        async for chunk in a_chunks(2, async_list(items)):
            result.append(chunk)
        self.assertEqual(result, [["a", "b"], ["c", "d"], ["e"]])

    async def test_with_falsy_values(self):
        """Test chunking with falsy values like 0, False, empty strings."""
        result = []
        items = [0, False, "", None, [], 1]
        async for chunk in a_chunks(2, async_list(items)):
            result.append(chunk)
        self.assertEqual(result, [[0, False], ["", None], [[], 1]])

    async def test_with_mixed_types(self):
        """Test chunking with mixed types."""
        result = []
        items = [1, "two", 3.0, None, {"key": "value"}]
        async for chunk in a_chunks(2, async_list(items)):
            result.append(chunk)
        self.assertEqual(result, [[1, "two"], [3.0, None], [{"key": "value"}]])
