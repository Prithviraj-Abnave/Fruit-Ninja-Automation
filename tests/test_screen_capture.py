import unittest
import threading
import numpy as np
from screen_capture import ScreenCapture


class TestScreenCapture(unittest.TestCase):
    def setUp(self):
        self.cap = ScreenCapture()

    def test_screen_capture_frame_format(self):
        """Verify screen capture returns a valid 3-channel BGR numpy array."""
        frame = self.cap.get_frame()
        self.assertIsInstance(frame, np.ndarray, "Captured frame must be a numpy ndarray")
        self.assertEqual(frame.ndim, 3, "Captured frame must have 3 dimensions (H, W, C)")
        self.assertEqual(frame.shape[2], 3, "Captured frame must have 3 color channels (BGR)")
        self.assertEqual(frame.dtype, np.uint8, "Captured frame data type must be uint8")
        self.assertGreater(frame.shape[0], 0, "Height must be > 0")
        self.assertGreater(frame.shape[1], 0, "Width must be > 0")

    def test_multithreaded_capture(self):
        """Ensure screen capture can be safely called across worker threads without deadlocks."""
        results = []
        errors = []

        def worker():
            try:
                frame = self.cap.get_frame()
                results.append(frame.shape)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
            self.assertFalse(t.is_alive(), "Worker thread hung during screen capture")

        self.assertEqual(len(errors), 0, f"Encountered thread errors: {errors}")
        self.assertEqual(len(results), 3, "All worker threads must successfully capture a frame")


if __name__ == "__main__":
    unittest.main()
