"""Tests for async_chunks function."""
import asyncio
import unittest

from ownjoo_toolkit.asynchronous.async_chunks import a_chunks


async def async_range(n: int):
    """Helper to generate async iterable from range."""
    for i in range(n):
        yield i


async def async_list(items: list):
    """Helper to generate async iterable from list."""
    for item in items:
        yield item


async def collect_chunks(chunk_size: int, async_iterable):
    """Helper to collect all chunks from async generator."""
    result = []
    async for chunk in a_chunks(chunk_size, async_iterable):
        result.append(chunk)
    return result


class TestAsyncChunks(unittest.TestCase):
    """Tests for a_chunks function."""

    def test_basic_chunking(self):
        """Test basic chunking with multiple complete chunks."""
        result = asyncio.run(collect_chunks(3, async_range(9)))
        self.assertEqual(result, [[0, 1, 2], [3, 4, 5], [6, 7, 8]])

    def test_partial_final_chunk(self):
        """Test that remaining items smaller than chunk_size are yielded."""
        result = asyncio.run(collect_chunks(3, async_range(7)))
        self.assertEqual(result, [[0, 1, 2], [3, 4, 5], [6]])

    def test_chunk_size_one(self):
        """Test chunking with size 1."""
        result = asyncio.run(collect_chunks(1, async_range(3)))
        self.assertEqual(result, [[0], [1], [2]])

    def test_chunk_size_larger_than_items(self):
        """Test chunk size larger than number of items."""
        result = asyncio.run(collect_chunks(10, async_range(3)))
        self.assertEqual(result, [[0, 1, 2]])

    def test_empty_async_iterable(self):
        """Test with empty async iterable."""
        result = asyncio.run(collect_chunks(3, async_range(0)))
        self.assertEqual(result, [])

    def test_single_item(self):
        """Test with single item."""
        result = asyncio.run(collect_chunks(3, async_range(1)))
        self.assertEqual(result, [[0]])

    def test_exact_multiple_of_chunk_size(self):
        """Test when items are exact multiple of chunk_size."""
        result = asyncio.run(collect_chunks(5, async_range(15)))
        self.assertEqual(
            result,
            [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14]],
        )

    def test_with_string_items(self):
        """Test chunking with non-numeric items."""
        items = ["a", "b", "c", "d", "e"]
        result = asyncio.run(collect_chunks(2, async_list(items)))
        self.assertEqual(result, [["a", "b"], ["c", "d"], ["e"]])

    def test_with_falsy_values(self):
        """Test chunking with falsy values like 0, False, empty strings."""
        items = [0, False, "", None, [], 1]
        result = asyncio.run(collect_chunks(2, async_list(items)))
        self.assertEqual(result, [[0, False], ["", None], [[], 1]])

    def test_with_mixed_types(self):
        """Test chunking with mixed types."""
        items = [1, "two", 3.0, None, {"key": "value"}]
        result = asyncio.run(collect_chunks(2, async_list(items)))
        self.assertEqual(result, [[1, "two"], [3.0, None], [{"key": "value"}]])
