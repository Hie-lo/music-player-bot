"""Deterministic queue rules with no Telegram or database dependency."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .models import DomainError, LoopMode, PlaybackSnapshot, PlaybackStatus, QueueItem


class QueueItemNotFound(DomainError):
    """Raised when a queue item id does not exist."""


class PlaybackQueue:
    """A single-writer queue for one chat.

    Persistence is intentionally outside this class. The caller persists the
    returned snapshot after each successful mutation.
    """

    def __init__(self, *, max_size: int = 100) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        self._max_size = max_size
        self._current: QueueItem | None = None
        self._queued: list[QueueItem] = []
        self._history: list[QueueItem] = []
        self._loop_mode = LoopMode.OFF
        self._status = PlaybackStatus.IDLE
        self._position_seconds = 0
        self._error_code: str | None = None

    @property
    def snapshot(self) -> PlaybackSnapshot:
        return PlaybackSnapshot(
            status=self._status,
            current=self._current,
            queued=tuple(self._queued),
            history=tuple(self._history),
            loop_mode=self._loop_mode,
            position_seconds=self._position_seconds,
            error_code=self._error_code,
        )

    def enqueue(self, item: QueueItem, *, position: int | None = None) -> None:
        if len(self._queued) >= self._max_size:
            raise DomainError("queue limit reached")
        if any(existing.item_id == item.item_id for existing in self._queued) or (
            self._current and self._current.item_id == item.item_id
        ):
            raise DomainError("queue item id already exists")
        if position is None:
            self._queued.append(item)
            return
        if position < 0 or position > len(self._queued):
            raise IndexError("queue position out of range")
        self._queued.insert(position, item)

    def enqueue_many(self, items: Iterable[QueueItem]) -> None:
        items = tuple(items)
        if len(self._queued) + len(items) > self._max_size:
            raise DomainError("queue limit reached")
        for item in items:
            self.enqueue(item)

    def start_next(self) -> QueueItem | None:
        if self._current is not None:
            raise DomainError("a track is already current")
        if not self._queued:
            self._status = PlaybackStatus.IDLE
            self._position_seconds = 0
            return None
        self._current = self._queued.pop(0)
        self._status = PlaybackStatus.BUFFERING
        self._position_seconds = 0
        self._error_code = None
        return self._current

    def set_status(self, status: PlaybackStatus) -> None:
        if status is PlaybackStatus.ERROR:
            raise DomainError("use fail() to set an error")
        self._status = status
        if status is not PlaybackStatus.PLAYING:
            self._error_code = None

    def update_position(self, seconds: int) -> None:
        if seconds < 0:
            raise DomainError("position must not be negative")
        self._position_seconds = seconds

    def set_loop_mode(self, mode: LoopMode) -> None:
        self._loop_mode = mode

    def finish_current(self) -> QueueItem | None:
        """Finish current playback and optionally requeue according to loop mode."""
        if self._current is None:
            return self.start_next()
        finished = self._current
        self._history.append(finished)
        if self._loop_mode is LoopMode.TRACK:
            self._queued.insert(0, finished)
        elif self._loop_mode is LoopMode.QUEUE:
            self._queued.append(finished)
        self._current = None
        self._position_seconds = 0
        self._status = PlaybackStatus.IDLE
        return self.start_next()

    def skip(self) -> QueueItem | None:
        if self._current is not None:
            self._history.append(self._current)
        self._current = None
        self._position_seconds = 0
        self._status = PlaybackStatus.IDLE
        self._error_code = None
        return self.start_next()

    def previous(self) -> QueueItem | None:
        if not self._history:
            return None
        if self._current is not None:
            self._queued.insert(0, self._current)
        self._current = self._history.pop()
        self._position_seconds = 0
        self._status = PlaybackStatus.BUFFERING
        self._error_code = None
        return self._current

    def remove(self, item_id: str) -> QueueItem:
        for index, item in enumerate(self._queued):
            if item.item_id == item_id:
                return self._queued.pop(index)
        raise QueueItemNotFound(item_id)

    def move(self, item_id: str, new_position: int) -> None:
        if new_position < 0 or new_position >= len(self._queued):
            raise IndexError("queue position out of range")
        item = self.remove(item_id)
        self._queued.insert(new_position, item)

    def clear(self) -> tuple[QueueItem, ...]:
        removed = tuple(self._queued)
        self._queued.clear()
        return removed

    def fail(self, error_code: str) -> None:
        if not error_code.strip():
            raise DomainError("error_code must not be empty")
        self._status = PlaybackStatus.ERROR
        self._error_code = error_code

    def recover(self) -> None:
        if self._status is not PlaybackStatus.ERROR:
            return
        self._status = PlaybackStatus.IDLE if self._current is None else PlaybackStatus.BUFFERING
        self._error_code = None

    def restore(self, snapshot: PlaybackSnapshot) -> None:
        """Restore durable state after restart with validation."""
        self._current = snapshot.current
        self._queued = list(snapshot.queued)
        self._history = list(snapshot.history)
        self._loop_mode = snapshot.loop_mode
        self._status = snapshot.status
        self._position_seconds = snapshot.position_seconds
        self._error_code = snapshot.error_code
        if len(self._queued) > self._max_size:
            raise DomainError("persisted queue exceeds configured max size")
        ids = [item.item_id for item in self._queued]
        if self._current:
            ids.append(self._current.item_id)
        if len(ids) != len(set(ids)):
            raise DomainError("persisted queue contains duplicate item ids")
