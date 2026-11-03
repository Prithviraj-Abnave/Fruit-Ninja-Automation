import os
import unittest
import numpy as np
from detect import FruitDetector


class TestFruitDetector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Prefer models/best.pt; fall back to yolov8n.pt for lightweight CI/local tests
        if os.path.exists("models/best.pt"):
            cls.model_path = "models/best.pt"
        else:
            cls.model_path = "yolov8n.pt"
        cls.detector = FruitDetector(cls.model_path, conf_threshold=0.3)

    def test_detector_inference_on_synthetic_frame(self):
        """Inference should execute smoothly on synthetic frames without raising exceptions."""
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = self.detector.detect(dummy_frame)
        self.assertIsInstance(detections, list, "Detections must be returned as a list")

    def test_detection_structure(self):
        """When detections are returned, verify expected dictionary structure."""
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = self.detector.detect(dummy_frame)
        for det in detections:
            self.assertIn("box", det)
            self.assertIn("conf", det)
            self.assertIn("class", det)
            self.assertIn("center", det)
            self.assertEqual(len(det["box"]), 4)
            self.assertEqual(len(det["center"]), 2)

    def test_draw_detections_returns_frame(self):
        """Drawing detections should return an image with identical shape and type."""
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_detections = [
            {
                "box": (50, 50, 150, 150),
                "conf": 0.95,
                "class": "Fruit",
                "center": (100, 100),
            },
            {
                "box": (200, 200, 300, 300),
                "conf": 0.88,
                "class": "Bomb",
                "center": (250, 250),
            },
        ]
        annotated = self.detector.draw_detections(dummy_frame.copy(), mock_detections)
        self.assertEqual(annotated.shape, dummy_frame.shape)
        self.assertEqual(annotated.dtype, dummy_frame.dtype)


if __name__ == "__main__":
    unittest.main()
