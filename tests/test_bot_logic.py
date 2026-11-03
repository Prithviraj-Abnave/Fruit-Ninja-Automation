import unittest
import math
from main import SimpleTracker, FruitNinjaBot


class TestBotLogic(unittest.TestCase):
    def setUp(self):
        self.tracker = SimpleTracker()

    def test_tracker_initial_frame(self):
        """Initial frame should return current detections with no velocity adjustments."""
        items = [
            {'center': (100, 200), 'class': 'Fruit', 'conf': 0.9, 'box': (90, 190, 110, 210)}
        ]
        compensated = self.tracker.get_velocity_compensated(items, current_time=1.0)
        self.assertEqual(len(compensated), 1)
        self.assertEqual(compensated[0]['center'], (100, 200))

    def test_tracker_velocity_extrapolation(self):
        """Tracker should project position forward based on detected velocity and latency."""
        frame1 = [{'center': (100, 200), 'class': 'Fruit'}]
        self.tracker.get_velocity_compensated(frame1, current_time=1.0)

        # Fruit moved right 10px and down 20px over 0.1s => vx=100px/s, vy=200px/s
        frame2 = [{'center': (110, 220), 'class': 'Fruit'}]
        # With latency = 0.05s, expected delta is (5px, 10px) => center: (115, 230)
        compensated = self.tracker.get_velocity_compensated(frame2, current_time=1.1, latency=0.05)
        self.assertEqual(len(compensated), 1)
        cx, cy = compensated[0]['center']
        self.assertEqual(cx, 115)
        self.assertEqual(cy, 230)

    def test_point_segment_dist(self):
        """Test geometric point-to-line-segment distance calculation."""
        bot_dummy = object.__new__(FruitNinjaBot)
        
        # Point directly on segment midpoint
        d1 = bot_dummy.point_segment_dist(50, 0, 0, 0, 100, 0)
        self.assertAlmostEqual(d1, 0.0)

        # Point 30 units perpendicularly away from midpoint
        d2 = bot_dummy.point_segment_dist(50, 30, 0, 0, 100, 0)
        self.assertAlmostEqual(d2, 30.0)

        # Point beyond segment endpoint
        d3 = bot_dummy.point_segment_dist(130, 0, 0, 0, 100, 0)
        self.assertAlmostEqual(d3, 30.0)

    def test_path_safety_with_bomb(self):
        """Test bomb avoidance: paths intersecting the bomb buffer must be flagged unsafe."""
        bot_dummy = object.__new__(FruitNinjaBot)
        bombs = [{'center': (100, 100)}]
        buffer = 40

        # Direct collision through bomb
        self.assertFalse(bot_dummy.is_path_safe((0, 100), (200, 100), bombs, buffer))

        # Safe swipe well outside bomb buffer
        self.assertTrue(bot_dummy.is_path_safe((0, 200), (200, 200), bombs, buffer))


if __name__ == "__main__":
    unittest.main()
