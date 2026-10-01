import unittest
from unittest.mock import Mock
from orbit.events import OrbitEventDecoder
from orbit.session import WheelSession
from orbit.controller import WheelController
from test_core import settings


class EventTests(unittest.TestCase):
    def test_fragmented_release_and_batched_press_keep_order(self):
        decoder = OrbitEventDecoder()
        self.assertEqual(decoder.feed(b'workspace>>2\ncustom>>orbit:pre'), [])
        self.assertEqual(decoder.feed(b'ss\ncustom>>orbit:rel'), ['show'])
        self.assertEqual(decoder.feed(b'ease\ncustom>>orbit:press\n'), ['release', 'show'])

    def test_unrelated_and_similar_names_are_ignored(self):
        decoder = OrbitEventDecoder()
        self.assertEqual(decoder.feed(b'custom>>orbit:probe\ncustom>>orbit:release:other\n'), [])

    def test_fast_tap_does_not_leave_active_wheel(self):
        session = WheelSession(settings())
        compositor, view, launcher = Mock(), Mock(), Mock()
        compositor.cursor.return_value = (100, 100)
        compositor.monitors.return_value = [dict(x=0, y=0, width=1920, height=1200, scale=1)]
        controller = WheelController(session, compositor, view, launcher)
        for command in OrbitEventDecoder().feed(b'custom>>orbit:press\ncustom>>orbit:release\n'):
            controller.handle(command)
        self.assertFalse(session.active)
        view.show.assert_called_once()
        view.hide.assert_called_once()
        launcher.launch.assert_not_called()

    def test_holding_stays_active_until_release_and_launches_once(self):
        session = WheelSession(settings())
        compositor, view, launcher = Mock(), Mock(), Mock()
        compositor.cursor.return_value = (100, 100)
        compositor.monitors.return_value = [dict(x=0, y=0, width=1920, height=1200, scale=1)]
        controller = WheelController(session, compositor, view, launcher)
        decoder = OrbitEventDecoder()
        for command in decoder.feed(b'custom>>orbit:press\n'):
            controller.handle(command)
        session.move((200, 100))
        self.assertTrue(session.active)
        launcher.launch.assert_not_called()
        view.hide.assert_not_called()
        compositor.cursor.return_value = (200, 100)
        for command in decoder.feed(b'custom>>orbit:release\ncustom>>orbit:release\n'):
            controller.handle(command)
        self.assertFalse(session.active)
        view.hide.assert_called_once()
        launcher.launch.assert_called_once()

    def test_escape_event_cancels_then_release_cannot_launch(self):
        session = WheelSession(settings())
        compositor, view, launcher = Mock(), Mock(), Mock()
        session.begin((100, 100))
        session.move((200, 100))
        controller = WheelController(session, compositor, view, launcher)
        for command in OrbitEventDecoder().feed(b'custom>>orbit:cancel\ncustom>>orbit:release\n'):
            controller.handle(command)
        self.assertFalse(session.active)
        launcher.launch.assert_not_called()
        compositor.cursor.assert_not_called()

    def test_oversized_incomplete_message_is_rejected(self):
        with self.assertRaises(ValueError):
            OrbitEventDecoder().feed(b'x' * 65537)
