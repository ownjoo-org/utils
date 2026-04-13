from typing import AsyncGenerator, AsyncIterator, TypeVar

T = TypeVar("T")


async def a_chunks(chunk_size: int, async_iterable: AsyncIterator[T]) -> AsyncGenerator[list[T], None]:
    """Yield successive chunks from an async iterable.

    Args:
        async_iterable: An async iterable to chunk
        chunk_size: Maximum size of each chunk

    Yields:
        Lists of up to chunk_size elements
    """
    chunk: list[T] = []
    async for item in async_iterable:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []

    # Yield remaining items
    if chunk:
        yield chunk
