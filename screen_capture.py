import mss
import numpy as np
import cv2
from typing import Optional, Tuple

class ScreenCapture:
    def __init__(self, region: Optional[Tuple[int, int, int, int]] = None):
        """
        region: (x, y, width, height). If None, captures entire primary monitor.
        """
        import threading
        self.local = threading.local()
        with mss.mss() as sct:
            if region:
                self.monitor = {"top": region[1], "left": region[0], "width": region[2], "height": region[3]}
            else:
                self.monitor = sct.monitors[1]  # Primary monitor

    def get_frame(self) -> np.ndarray:
        if not hasattr(self.local, 'sct'):
            self.local.sct = mss.mss()
            
        # Capture screen
        screenshot = self.local.sct.grab(self.monitor)
        # Convert to numpy array and from BGRA to BGR
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame

if __name__ == "__main__":
    # Test capture
    cap = ScreenCapture()
    import time
    start_time = time.time()
    frames = 0
    while frames < 100:
        frame = cap.get_frame()
        frames += 1
        if frames % 20 == 0:
            print(f"Captured {frames} frames...")
    
    end_time = time.time()
    print(f"Average FPS: {frames / (end_time - start_time):.2f}")
    cv2.imshow("Test Capture", cv2.resize(frame, (640, 360)))
    cv2.waitKey(2000)
    cv2.destroyAllWindows()
