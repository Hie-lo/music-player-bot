"""Application ports; adapters implement these protocols."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol

from music_player_bot.domain.models import PlaybackSnapshot, Track


@dataclass(frozen=True, slots=True)
class ResolvedMedia:
    track: Track
    playable_url: str
    expires_at_epoch: int | None = None
    supports_video: bool = False


class MediaResolverPort(Protocol):
    async def resolve(self, query_or_url: str) -> ResolvedMedia: ...


class PlaybackEnginePort(Protocol):
    async def join(self, chat_id: int) -> None: ...

    async def play(self, chat_id: int, media: ResolvedMedia, *, position_seconds: int = 0) -> None: ...

    async def pause(self, chat_id: int) -> None: ...

    async def resume(self, chat_id: int) -> None: ...

    async def skip(self, chat_id: int) -> None: ...

    async def stop(self, chat_id: int) -> None: ...

    async def leave(self, chat_id: int) -> None: ...


class PlaybackSnapshotRepository(Protocol):
    async def save(self, chat_id: int, snapshot: PlaybackSnapshot) -> None: ...

    async def load(self, chat_id: int) -> PlaybackSnapshot | None: ...


Notification = Callable[[int, str], Awaitable[None]]
