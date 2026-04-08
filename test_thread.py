import threading
from screen_capture import ScreenCapture
import time

c = ScreenCapture()
print("Initialized ScreenCapture")

def f():
    print("Thread started")
    frame = c.get_frame()
    print("Got frame:", frame.shape)

t = threading.Thread(target=f)
t.start()
t.join(3)
if t.is_alive():
    print("Thread HUNG!")
else:
    print("Thread finished successfully")
