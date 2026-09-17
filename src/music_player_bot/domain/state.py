"""Validated playback state transitions."""

from __future__ import annotations

from .models import DomainError, PlaybackStatus


_ALLOWED: dict[PlaybackStatus, set[PlaybackStatus]] = {
    PlaybackStatus.IDLE: {PlaybackStatus.RESOLVING, PlaybackStatus.JOINING_CALL, PlaybackStatus.IDLE},
    PlaybackStatus.RESOLVING: {PlaybackStatus.BUFFERING, PlaybackStatus.ERROR, PlaybackStatus.IDLE},
    PlaybackStatus.BUFFERING: {
        PlaybackStatus.JOINING_CALL,
        PlaybackStatus.PLAYING,
        PlaybackStatus.ERROR,
        PlaybackStatus.IDLE,
    },
    PlaybackStatus.JOINING_CALL: {
        PlaybackStatus.PLAYING,
        PlaybackStatus.ERROR,
        PlaybackStatus.IDLE,
    },
    PlaybackStatus.PLAYING: {
        PlaybackStatus.PAUSED,
        PlaybackStatus.STOPPING,
        PlaybackStatus.BUFFERING,
        PlaybackStatus.ERROR,
        PlaybackStatus.IDLE,
    },
    PlaybackStatus.PAUSED: {
        PlaybackStatus.PLAYING,
        PlaybackStatus.STOPPING,
        PlaybackStatus.ERROR,
        PlaybackStatus.IDLE,
    },
    PlaybackStatus.STOPPING: {PlaybackStatus.IDLE, PlaybackStatus.ERROR},
    PlaybackStatus.ERROR: {
        PlaybackStatus.RESOLVING,
        PlaybackStatus.BUFFERING,
        PlaybackStatus.IDLE,
        PlaybackStatus.ERROR,
    },
}


def ensure_transition(current: PlaybackStatus, target: PlaybackStatus) -> None:
    if target not in _ALLOWED[current]:
        raise DomainError(f"invalid playback transition: {current} -> {target}")
