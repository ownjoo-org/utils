"""Tests for oj_toolkit.diagnostics.install_exception_visibility.

The real value is preventing silent failures. These tests exercise each of
the five channels the harness monitors: sys.excepthook, threading.excepthook,
sys.unraisablehook, asyncio loop exception handler, and the
"Task exception was never retrieved" path.
"""

from __future__ import annotations

import asyncio
import logging
import sys
import threading
import unittest

from oj_toolkit import diagnostics


class TestExceptionVisibility(unittest.TestCase):
    """Every hook a service can install, asserted."""

    def setUp(self) -> None:
        # Force re-installation for each test; the real function is
        # idempotent by design but tests want a known starting state.
        diagnostics._INSTALLED = False  # pylint: disable=protected-access

    def test_idempotent(self) -> None:
        diagnostics.install_exception_visibility()
        diagnostics.install_exception_visibility()  # must not raise
        diagnostics.install_exception_visibility()

    def test_sys_excepthook_routes_to_logger(self) -> None:
        diagnostics.install_exception_visibility()
        with self.assertLogs(diagnostics.logger, level=logging.ERROR) as caplog:
            try:
                raise RuntimeError('top-level boom')
            except RuntimeError:
                sys.excepthook(*sys.exc_info())  # type: ignore[misc]
        self.assertTrue(
            any('uncaught top-level' in r.getMessage() for r in caplog.records),
            caplog.output,
        )

    def test_threading_excepthook_routes_to_logger(self) -> None:
        diagnostics.install_exception_visibility()
        errors: list[str] = []

        def _boom() -> None:
            raise RuntimeError('thread boom')

        class _Capture(logging.Handler):
            """Logging handler that records emitted messages for assertion."""
            def emit(self, record: logging.LogRecord) -> None:
                errors.append(record.getMessage())

        diagnostics.logger.addHandler(_Capture())
        try:
            t = threading.Thread(target=_boom, name='victim')
            t.start()
            t.join()
        finally:
            diagnostics.logger.handlers = [
                h for h in diagnostics.logger.handlers if not isinstance(h, _Capture)
            ]
        self.assertTrue(
            any("thread 'victim'" in m for m in errors),
            f'expected thread error, got: {errors}',
        )

    def test_calling_install_twice_is_safe(self) -> None:
        """Belt-and-suspenders: second install neither resets hooks nor errors."""
        diagnostics.install_exception_visibility()
        first_hook = sys.excepthook
        diagnostics.install_exception_visibility()
        self.assertIs(first_hook, sys.excepthook)

    def test_unraisablehook_routes_to_logger(self) -> None:
        diagnostics.install_exception_visibility()

        class _Bogus:  # pylint: disable=too-few-public-methods
            """Stand-in object for the finalizer whose exception triggered the hook."""
            def __repr__(self) -> str:
                return '<bogus>'

        with self.assertLogs(diagnostics.logger, level=logging.ERROR) as caplog:
            sys.unraisablehook(
                type(
                    'unraisable',
                    (),
                    {
                        'exc_type': RuntimeError,
                        'exc_value': RuntimeError('death by __del__'),
                        'exc_traceback': None,
                        'object': _Bogus(),
                        'err_msg': None,
                    },
                )()
            )
        self.assertTrue(
            any('unraisable' in r.getMessage() for r in caplog.records),
            caplog.output,
        )


class TestAsyncioExceptionHandler(unittest.IsolatedAsyncioTestCase):
    """Asyncio-specific coverage for the visibility harness."""

    async def asyncSetUp(self) -> None:
        diagnostics._INSTALLED = False  # pylint: disable=protected-access

    async def test_handler_installed_on_current_loop(self) -> None:
        """After install, the running loop has our handler."""
        diagnostics.install_exception_visibility()
        loop = asyncio.get_running_loop()
        # pylint: disable-next=protected-access
        self.assertIs(loop.get_exception_handler(), diagnostics._asyncio_exception_handler)

    async def test_asyncio_task_failure_routes_to_logger(self) -> None:
        """A task that raises and is awaited surfaces normally. A task that
        raises and is NEVER awaited only surfaces via the exception handler
        (or GC). This test installs the handler on the current loop and
        feeds it a simulated exception context."""
        diagnostics.install_exception_visibility()

        loop = asyncio.get_running_loop()
        # Install may have missed this loop if the harness was created first
        # by the test itself; do it explicitly so the assertion is clean.
        # pylint: disable-next=protected-access
        loop.set_exception_handler(diagnostics._asyncio_exception_handler)

        with self.assertLogs(diagnostics.logger, level=logging.ERROR) as caplog:
            exc = ValueError('async boom')
            loop.call_exception_handler({
                'message': 'unit-test simulated',
                'exception': exc,
            })
            await asyncio.sleep(0)  # yield so handler runs
        self.assertTrue(
            any('unit-test simulated' in r.getMessage() for r in caplog.records),
            caplog.output,
        )


class TestStrictVisibility(unittest.TestCase):
    """``strict_visibility`` context manager fails on silent-failure channels."""

    def setUp(self) -> None:
        diagnostics._INSTALLED = False  # pylint: disable=protected-access

    def test_passes_when_nothing_goes_wrong(self) -> None:
        with diagnostics.strict_visibility():
            logging.getLogger('noisy').info('fine')

    def test_fails_on_error_log(self) -> None:
        with self.assertRaises(AssertionError) as cm:
            with diagnostics.strict_visibility():
                logging.getLogger('noisy').error('something bad')
        self.assertIn('ERROR log', str(cm.exception))

    def test_fails_on_thread_death(self) -> None:
        def _boom() -> None:
            raise RuntimeError('thread boom')

        with self.assertRaises(AssertionError) as cm:
            with diagnostics.strict_visibility():
                thread = threading.Thread(target=_boom, name='victim')
                thread.start()
                thread.join()
        self.assertIn("thread 'victim' died", str(cm.exception))

    def test_fail_on_error_log_disabled(self) -> None:
        """With fail_on_error_log=False, ERROR logs don't trip the block."""
        with diagnostics.strict_visibility(fail_on_error_log=False):
            logging.getLogger('noisy').error('logged but tolerated')


class TestStrictVisibilityAsyncio(unittest.IsolatedAsyncioTestCase):
    """Async-specific coverage for ``strict_visibility``."""

    async def asyncSetUp(self) -> None:
        diagnostics._INSTALLED = False  # pylint: disable=protected-access

    async def test_fails_on_unawaited_task_exception(self) -> None:
        """A task created but never awaited that raises must fail the block."""
        with self.assertRaises(AssertionError) as cm:
            with diagnostics.strict_visibility():
                async def _boom() -> None:
                    raise ValueError('async boom')

                task = asyncio.create_task(_boom())
                await asyncio.sleep(0.05)  # let it run and fail
                del task  # let GC trigger the "never retrieved" path
        self.assertIn('async boom', str(cm.exception))

    async def test_strict_ok_when_task_succeeds(self) -> None:
        """Successful tasks don't trip the check."""
        with diagnostics.strict_visibility():
            async def _ok() -> int:
                return 42

            result = await asyncio.create_task(_ok())
        self.assertEqual(result, 42)


if __name__ == '__main__':
    unittest.main()
