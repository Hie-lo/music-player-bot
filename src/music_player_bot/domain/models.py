"""Immutable domain values used by queue and playback logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum


class DomainError(ValueError):
    """Base error for invalid domain operations."""


class LoopMode(StrEnum):
    OFF = "off"
    TRACK = "track"
    QUEUE = "queue"


class PlaybackStatus(StrEnum):
    IDLE = "idle"
    RESOLVING = "resolving"
    BUFFERING = "buffering"
    JOINING_CALL = "joining_call"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Track:
    """A logical media item; it does not contain a provider's expiring URL."""

    track_id: str
    title: str
    duration_seconds: int | None = None
    artist: str | None = None
    album: str | None = None
    thumbnail_url: str | None = None
    source_url: str | None = None
    source_platform: str = "unknown"
    is_video_available: bool = False

    def __post_init__(self) -> None:
        if not self.track_id.strip():
            raise DomainError("track_id must not be empty")
        if not self.title.strip():
            raise DomainError("title must not be empty")
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise DomainError("duration_seconds must not be negative")
        if not self.source_platform.strip():
            raise DomainError("source_platform must not be empty")


@dataclass(frozen=True, slots=True)
class QueueItem:
    item_id: str
    track: Track
    requested_by: int
    added_at: datetime

    @classmethod
    def create(cls, item_id: str, track: Track, requested_by: int) -> "QueueItem":
        if not item_id.strip():
            raise DomainError("item_id must not be empty")
        if requested_by == 0:
            raise DomainError("requested_by must not be zero")
        return cls(item_id, track, requested_by, datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class PlaybackSnapshot:
    status: PlaybackStatus
    current: QueueItem | None
    queued: tuple[QueueItem, ...]
    history: tuple[QueueItem, ...]
    loop_mode: LoopMode
    position_seconds: int = 0
    error_code: str | None = None

    def __post_init__(self) -> None:
        if self.position_seconds < 0:
            raise DomainError("position_seconds must not be negative")
        if self.status is PlaybackStatus.ERROR and not self.error_code:
            raise DomainError("error_code is required for ERROR status")
        if self.status is not PlaybackStatus.ERROR and self.error_code:
            raise DomainError("error_code is only valid for ERROR status")
