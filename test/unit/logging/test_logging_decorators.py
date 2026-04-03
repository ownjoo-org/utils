from asyncio import run
from logging import INFO, getLogger
import unittest

from typing import Generator, AsyncGenerator

from ownjoo_toolkit.logging.decorators import timed_generator, timed_async_generator


class TestLoggingDecorators(unittest.TestCase):
    def test_should_import(self):
        @timed_generator(log_progress=True, log_level=INFO, log_progress_interval=1, logger=getLogger(__name__))
        def log_something() -> Generator[int, None, None]:
            yield 0

        for each in log_something():
            self.assertIsNotNone(each)


    def test_should_import_async(self):
        async def run_me():
            @timed_async_generator(log_progress=True, log_level=INFO, log_progress_interval=1, logger=getLogger(__name__))
            async def log_something() -> AsyncGenerator[int, None]:
                yield 0

            async for each in log_something():
                self.assertIsNotNone(each)
        run(run_me())


if __name__ == '__main__':
    unittest.main()
