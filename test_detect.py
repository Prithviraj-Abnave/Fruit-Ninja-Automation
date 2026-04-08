import threading
import time
import numpy as np
import cv2
from detect import FruitDetector

print("Loading model...")
detector = FruitDetector("models/best.pt")
print("Model loaded.")
frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

def f():
    print("Thread started, running inference...")
    try:
        dets = detector.detect(frame)
        print("Inference done. Detections:", len(dets))
    except Exception as e:
        print("Inference error:", e)
    
    print("Testing cv2.imshow...")
    try:
        cv2.imshow("Debug View", frame)
        cv2.waitKey(1)
        print("cv2.imshow success.")
    except Exception as e:
        print("cv2.imshow error:", e)

t = threading.Thread(target=f)
t.start()
t.join(10)
if t.is_alive():
    print("Thread HUNG!")
else:
    print("Thread finished.")
