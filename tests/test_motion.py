import unittest
from orbit.motion import WheelMotion


class MotionTests(unittest.TestCase):
    def test_open_and_close_stop_at_endpoints(self):
        motion = WheelMotion(7)
        motion.show(10)
        self.assertTrue(motion.advance(10.05))
        self.assertGreater(motion.visibility.value, 0)
        self.assertLess(motion.visibility.value, 1)
        self.assertFalse(motion.advance(10.2))
        self.assertEqual(motion.scale, 1)
        motion.hide(11)
        self.assertTrue(motion.advance(11.04))
        self.assertFalse(motion.advance(11.2))
        self.assertEqual(motion.visibility.value, 0)

    def test_reopening_during_close_has_no_opacity_jump(self):
        motion = WheelMotion(7)
        motion.show(10)
        motion.advance(11)
        motion.hide(11)
        motion.advance(11.04)
        previous = motion.visibility.value
        motion.show(11.04)
        self.assertEqual(motion.visibility.value, previous)
        motion.advance(11.08)
        self.assertGreater(motion.visibility.value, previous)
        self.assertFalse(motion.advance(12))

    def test_hover_crossfade_retargets_from_current_values(self):
        motion = WheelMotion(7)
        motion.select(0, 10)
        motion.advance(10.04)
        value = motion.wedges[0].value
        motion.select(1, 10.04)
        self.assertEqual(motion.wedges[0].value, value)
        motion.advance(10.08)
        self.assertLess(motion.wedges[0].value, value)
        self.assertGreater(motion.wedges[1].value, 0)
        motion.advance(11)
        self.assertEqual([w.value for w in motion.wedges], [0, 1, 0, 0, 0, 0, 0])

    def test_reduced_motion_settles_immediately(self):
        motion = WheelMotion(7, enabled=False)
        motion.show(10)
        motion.select(3, 10)
        self.assertFalse(motion.advance(10))
        self.assertEqual(motion.visibility.value, 1)
        self.assertEqual(motion.wedges[3].value, 1)
        motion.hide(10)
        self.assertFalse(motion.advance(10))
        self.assertEqual(motion.visibility.value, 0)
