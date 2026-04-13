"""Asyncio-compatible logging handlers for ownjoo-org projects."""

import asyncio
import logging

from oj_toolkit.logging.formatters import HumanFormatter


class BroadcastHandler(logging.Handler):
    """
    Forwards log records to all active asyncio.Queue subscribers.

    Intended for log-streaming use cases (e.g. SSE endpoints): attach one
    instance to the root logger, then subscribe/unsubscribe per-client queues
    at request time.

    Usage::

        from oj_toolkit.logging import BroadcastHandler

        handler = BroadcastHandler()
        logging.getLogger().addHandler(handler)

        # in a request handler:
        q = handler.subscribe()
        try:
            msg = await q.get()
            ...
        finally:
            handler.unsubscribe(q)

    Thread-safety note: ``emit()`` calls ``put_nowait`` directly, which is
    safe when invoked from the event loop thread (i.e. from within a
    coroutine).  If you log from background threads, wrap with
    ``loop.call_soon_threadsafe`` in a subclass instead.
    """

    def __init__(self, maxsize: int = 500) -> None:
        super().__init__()
        self.setFormatter(HumanFormatter())
        self._maxsize = maxsize
        self._subscribers: set[asyncio.Queue] = set()

    def subscribe(self) -> "asyncio.Queue[str]":
        """Register a new subscriber; returns its dedicated queue."""
        q: asyncio.Queue[str] = asyncio.Queue(maxsize=self._maxsize)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: "asyncio.Queue[str]") -> None:
        """Deregister a subscriber queue (call this on client disconnect)."""
        self._subscribers.discard(q)

    def emit(self, record: logging.LogRecord) -> None:
        if not self._subscribers:
            return
        msg = self.format(record)
        dead: set[asyncio.Queue] = set()
        for q in self._subscribers:
            try:
                q.put_nowait(msg)
            except asyncio.QueueFull:
                # Slow / stalled consumer — drop it rather than block the logger.
                dead.add(q)
        self._subscribers -= dead
