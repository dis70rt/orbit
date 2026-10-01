import math
import unittest
from unittest.mock import Mock
from orbit.geometry import segment_at, monitor_at, monitor_bounds
from orbit.settings import Settings
from orbit.session import WheelSession
from orbit.controller import WheelController


def settings():
    return Settings.from_dict({'shortcuts': [
        {'label': str(i), 'icon': 'folder', 'type': 'command', 'value': ['echo', str(i)]}
        for i in range(8)]})


class GeometryTests(unittest.TestCase):
    def test_clockwise_segments_and_dead_zone(self):
        for count in (6, 8, 12):
            for i in range(count):
                a = i * math.tau / count - math.pi / 2
                self.assertEqual(segment_at(100 * math.cos(a), 100 * math.sin(a), count, 65), i)
        self.assertIsNone(segment_at(65, 0, 8, 65))
        self.assertIsNone(segment_at(0, 0, 8, 65))

    def test_rotated_scaled_monitor_with_negative_origin(self):
        monitor = {'x': -600, 'y': 0, 'width': 1600, 'height': 1200, 'scale': 2, 'transform': 1}
        self.assertEqual(monitor_bounds(monitor), (-600, 0, 600, 800))
        self.assertIs(monitor_at([monitor], (-1, 799)), monitor)
        with self.assertRaises(RuntimeError):
            monitor_at([monitor], (0, 799))


class SessionTests(unittest.TestCase):
    def test_release_uses_final_point_and_is_idempotent(self):
        session = WheelSession(settings())
        session.begin((500, 500))
        session.move((500, 400))
        self.assertEqual(session.release((600, 500)).label, '2')
        self.assertIsNone(session.release((600, 500)))

    def test_center_and_escape_cancel(self):
        session = WheelSession(settings())
        session.begin((500, 500))
        session.move((700, 500))
        self.assertIsNone(session.release((501, 501)))
        session.begin((0, 0))
        session.cancel()
        self.assertIsNone(session.release((0, -100)))

    def test_duplicate_press_preserves_origin(self):
        session = WheelSession(settings())
        session.begin((1, 2))
        session.begin((3, 4))
        self.assertEqual(session.origin, (1, 2))


class ConfigurationTests(unittest.TestCase):
    def test_rejects_invalid_and_nonfinite_values(self):
        good = {'shortcuts': [dict(label='A', icon='folder', type='command', value=['echo'])] * 2}
        for field, value in [('radius', math.nan), ('dead_zone', -1), ('accent', [1, 2, 3])]:
            with self.assertRaises(ValueError):
                Settings.from_dict({**good, field: value})
        for value in ('echo dangerous', [], ['echo', 1]):
            with self.assertRaises(ValueError):
                Settings.from_dict({'shortcuts': [dict(label='A', icon='folder', type='command', value=value)] * 2})


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.session = WheelSession(settings())
        self.compositor, self.view, self.launcher = Mock(), Mock(), Mock()
        self.controller = WheelController(self.session, self.compositor, self.view, self.launcher)
        self.session.begin((100, 100))

    def test_hides_before_launch_and_never_launches_twice(self):
        self.compositor.cursor.return_value = (200, 100)
        self.launcher.launch.side_effect = lambda shortcut: self.assertFalse(self.session.active)
        self.controller.handle('release')
        self.controller.handle('release')
        self.launcher.launch.assert_called_once()
        self.view.hide.assert_called_once()

    def test_query_failure_closes_without_launch(self):
        self.compositor.cursor.side_effect = RuntimeError('disconnected')
        with self.assertRaises(RuntimeError):
            self.controller.handle('release')
        self.assertFalse(self.session.active)
        self.view.hide.assert_called_once()
        self.launcher.launch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
