from concurrent.futures import Future
import unittest
from unittest.mock import Mock
from orbit.cursor import CursorTracker


class CursorTests(unittest.TestCase):
    def setUp(self):
        self.loop, self.update = Mock(), Mock()
        self.tracker = CursorTracker(Mock(), self.update, self.loop)
        self.tracker.executor.shutdown(wait=False)
        self.tracker.executor = Mock()
        self.future = Future()
        self.tracker.executor.submit.return_value = self.future

    def test_stop_removes_timer_and_rejects_old_generation(self):
        self.tracker.start()
        generation = self.tracker.generation
        self.tracker._tick(generation)
        self.tracker.stop()
        self.future.set_result((100, 200))
        self.assertFalse(self.tracker._tick(generation))
        self.update.assert_not_called()
        self.loop.source_remove.assert_called_once()
        self.assertIsNone(self.tracker.source_id)

    def test_waits_for_query_then_updates_without_parallel_queries(self):
        self.tracker.start()
        generation = self.tracker.generation
        self.tracker._tick(generation)
        self.tracker._tick(generation)
        self.tracker.executor.submit.assert_called_once()
        self.future.set_result((100, 200))
        self.tracker._tick(generation)
        self.update.assert_called_once_with((100, 200))

    def test_failed_query_does_not_deliver_invalid_position(self):
        self.tracker.start()
        generation = self.tracker.generation
        self.tracker._tick(generation)
        self.future.set_exception(ConnectionError('disconnected'))
        self.assertTrue(self.tracker._tick(generation))
        self.update.assert_not_called()
