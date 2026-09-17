"""Single-writer async actor for one chat playback session."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

T = TypeVar("T")
Command = Callable[[], Awaitable[T]]


class ActorClosedError(RuntimeError):
    """Raised when submitting work to a stopped actor."""


class ChatPlaybackActor:
    """Serialize mutations for one chat and preserve command ordering."""

    def __init__(self, chat_id: int) -> None:
        self.chat_id = chat_id
        self._queue: asyncio.Queue[tuple[Command[object], asyncio.Future[object]]] = asyncio.Queue()
        self._task: asyncio.Task[None] | None = None
        self._closed = False

    async def start(self) -> None:
        if self._task is None:
            self._closed = False
            self._task = asyncio.create_task(self._run(), name=f"playback-actor:{self.chat_id}")

    async def _run(self) -> None:
        while True:
            command, future = await self._queue.get()
            if future.cancelled():
                self._queue.task_done()
                continue
            try:
                result = await command()
            except asyncio.CancelledError:
                if not future.done():
                    future.cancel()
                self._queue.task_done()
                raise
            except Exception as exc:  # Propagate to the submitter; actor remains alive.
                if not future.done():
                    future.set_exception(exc)
            else:
                if not future.done():
                    future.set_result(result)
            finally:
                self._queue.task_done()

    async def submit(self, command: Command[T]) -> T:
        if self._closed or self._task is None:
            raise ActorClosedError(f"actor {self.chat_id} is not running")
        loop = asyncio.get_running_loop()
        future: asyncio.Future[object] = loop.create_future()
        await self._queue.put((command, future))
        result = await future
        return result  # type: ignore[return-value]

    async def stop(self) -> None:
        self._closed = True
        if self._task is None:
            return
        task = self._task
        self._task = None
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        while not self._queue.empty():
            _, future = self._queue.get_nowait()
            if not future.done():
                future.set_exception(ActorClosedError(f"actor {self.chat_id} stopped"))
            self._queue.task_done()


class ActorManager:
    """Own actors and ensure one actor exists per chat id."""

    def __init__(self) -> None:
        self._actors: dict[int, ChatPlaybackActor] = {}
        self._lock = asyncio.Lock()

    async def get(self, chat_id: int) -> ChatPlaybackActor:
        async with self._lock:
            actor = self._actors.get(chat_id)
            if actor is None:
                actor = ChatPlaybackActor(chat_id)
                await actor.start()
                self._actors[chat_id] = actor
            return actor

    async def stop_all(self) -> None:
        async with self._lock:
            actors = tuple(self._actors.values())
            self._actors.clear()
        await asyncio.gather(*(actor.stop() for actor in actors))
