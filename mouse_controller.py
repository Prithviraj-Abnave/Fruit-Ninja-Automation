import pyautogui
import time
import random
import numpy as np
import math

class MouseController:
    def __init__(self, speed=0.06):
        # Reduced pause for lower latency
        pyautogui.PAUSE = 0.001 
        pyautogui.FAILSAFE = False # Disabled to prevent crash on edge swipes
        pyautogui.MINIMUM_DURATION = 0
        pyautogui.MINIMUM_SLEEP = 0
        self.speed = speed

    def test_move(self):
        """Perform a tiny move to verify control on startup."""
        curr_x, curr_y = pyautogui.position()
        pyautogui.moveRel(5, 5, duration=0.1)
        pyautogui.moveRel(-5, -5, duration=0.1)

    def move_to(self, x, y):
        pyautogui.moveTo(x, y, duration=0)

    def swipe(self, x1, y1, x2, y2, style="curve"):
        """
        Performs a swipe from (x1, y1) to (x2, y2).
        Style: 'straight' or 'curve'
        """
        if style == "straight":
            pyautogui.moveTo(x1, y1)
            pyautogui.dragTo(x2, y2, duration=self.speed, button='left')
        else:
            self._swipe_curve(x1, y1, x2, y2)

    def _swipe_curve(self, x1, y1, x2, y2):
        """
        Simulates a curved swipe using intermediate points.
        """
        # Calculate a control point for a quadratic Bezier curve
        # Offset the midpoint perpendicularly
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Offset amount (randomized for natural feel)
        offset = random.randint(30, 80) * random.choice([-1, 1])
        
        # Perpendicular vector
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx**2 + dy**2)
        if length == 0: return
        
        nx = -dy / length
        ny = dx / length
        
        cx = mid_x + nx * offset
        cy = mid_y + ny * offset
        
        # Draw the curve
        pyautogui.moveTo(x1, y1)
        pyautogui.mouseDown()
        time.sleep(0.005) # Touch register delay
        
        steps = 7  # Reduced from 15 for faster response
        duration_per_step = self.speed / steps
        
        for i in range(1, steps + 1):
            t = i / steps
            # Bezier formula: (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
            curr_x = (1-t)**2 * x1 + 2*(1-t)*t * cx + t**2 * x2
            curr_y = (1-t)**2 * y1 + 2*(1-t)*t * cy + t**2 * y2
            pyautogui.moveTo(curr_x, curr_y, duration=duration_per_step)
            
        pyautogui.mouseUp()


    def _catmull_rom_spline(self, p0, p1, p2, p3, num_points):
        res = []
        for i in range(num_points):
            t = i / num_points
            t2 = t * t
            t3 = t2 * t
            q0 = -t3 + 2.0*t2 - t
            q1 = 3.0*t3 - 5.0*t2 + 2.0
            q2 = -3.0*t3 + 4.0*t2 + t
            q3 = t3 - t2
            x = 0.5 * (p0[0]*q0 + p1[0]*q1 + p2[0]*q2 + p3[0]*q3)
            y = 0.5 * (p0[1]*q0 + p1[1]*q1 + p2[1]*q2 + p3[1]*q3)
            res.append((int(x), int(y)))
        return res

    def _generate_smooth_path(self, points):
        if len(points) < 3: return points
        pts = [points[0]] + points + [points[-1]]
        smooth_points = []
        for i in range(1, len(pts) - 2):
            p0, p1, p2, p3 = pts[i-1], pts[i], pts[i+1], pts[i+2]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            steps = max(1, int(dist / 15)) # High density curve steps
            smooth_points.extend(self._catmull_rom_spline(p0, p1, p2, p3, steps))
        smooth_points.append(points[-1])
        return smooth_points

    def swipe_chain(self, points, smooth=True):
        if not points: return
        
        # Optionally convert sharp nodes into a smooth mathematical curve
        if smooth and len(points) >= 3:
            points = self._generate_smooth_path(points)
        
        pyautogui.moveTo(points[0][0], points[0][1])
        pyautogui.mouseDown()
        time.sleep(0.005) # Minimal touch register
        
        for i in range(1, len(points)):
            p_prev = points[i-1]
            p_next = points[i]
            
            dx = p_next[0] - p_prev[0]
            dy = p_next[1] - p_prev[1]
            distance = math.hypot(dx, dy)
            
            # ~30 pixel step spacing ensures low tracking lag but robust line formation
            steps = max(1, int(distance / 30))
            
            for step in range(1, steps + 1):
                t = step / steps
                curr_x = int(p_prev[0] + dx * t)
                curr_y = int(p_prev[1] + dy * t)
                pyautogui.moveTo(curr_x, curr_y)
                # Intentionally NO sleep in this loop. Let the python loop iteration act as the micro-delay.
            
        time.sleep(0.005) # Tiny hold at the end
        pyautogui.mouseUp()

    def click(self, x, y):

        pyautogui.click(x, y)

if __name__ == "__main__":
    # Safety test: move mouse in a circle
    ctrl = MouseController(speed=0.1)
    print("Starting mouse test in 2 seconds. Move mouse to corner to abort.")
    time.sleep(2)
    center_x, center_y = pyautogui.position()
    ctrl.swipe(center_x, center_y, center_x + 200, center_y - 100, style="curve")
    print("Test complete.")
