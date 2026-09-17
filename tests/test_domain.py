from __future__ import annotations

import asyncio
import unittest

from music_player_bot.application.actor import ActorManager
from music_player_bot.domain.models import DomainError, LoopMode, PlaybackStatus, QueueItem, Track
from music_player_bot.domain.queue import PlaybackQueue
from music_player_bot.domain.state import ensure_transition


def item(number: int) -> QueueItem:
    track = Track(track_id=f"track-{number}", title=f"Track {number}", source_platform="test")
    return QueueItem.create(f"item-{number}", track, requested_by=number)


class QueueTests(unittest.TestCase):
    def test_queue_start_finish_and_history(self) -> None:
        queue = PlaybackQueue(max_size=3)
        queue.enqueue(item(1))
        queue.enqueue(item(2))
        current = queue.start_next()
        self.assertEqual(current.item_id, "item-1")
        queue.set_status(PlaybackStatus.PLAYING)
        next_item = queue.finish_current()
        self.assertEqual(next_item.item_id, "item-2")
        self.assertEqual(queue.snapshot.history[0].item_id, "item-1")

    def test_loop_track_starts_current_again(self) -> None:
        queue = PlaybackQueue(max_size=3)
        queue.enqueue(item(1))
        queue.set_loop_mode(LoopMode.TRACK)
        queue.start_next()
        current = queue.finish_current()
        self.assertEqual(current.item_id, "item-1")
        self.assertEqual(queue.snapshot.current.item_id, "item-1")
        self.assertEqual(queue.snapshot.queued, ())

    def test_move_remove_and_limit(self) -> None:
        queue = PlaybackQueue(max_size=2)
        queue.enqueue(item(1))
        queue.enqueue(item(2))
        with self.assertRaises(DomainError):
            queue.enqueue(item(3))
        queue.move("item-2", 0)
        self.assertEqual(queue.snapshot.queued[0].item_id, "item-2")
        removed = queue.remove("item-2")
        self.assertEqual(removed.item_id, "item-2")

    def test_invalid_state_transition_is_rejected(self) -> None:
        with self.assertRaises(DomainError):
            ensure_transition(PlaybackStatus.IDLE, PlaybackStatus.PAUSED)


class ActorTests(unittest.IsolatedAsyncioTestCase):
    async def test_actor_serializes_commands(self) -> None:
        manager = ActorManager()
        actor = await manager.get(1)
        events: list[str] = []

        async def first() -> str:
            events.append("first-start")
            await asyncio.sleep(0.01)
            events.append("first-end")
            return "one"

        async def second() -> str:
            events.append("second")
            return "two"

        results = await asyncio.gather(actor.submit(first), actor.submit(second))
        self.assertEqual(results, ["one", "two"])
        self.assertEqual(events, ["first-start", "first-end", "second"])
        await manager.stop_all()
