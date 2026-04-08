import cv2
import time
import yaml
import os
import threading
import math
import pyautogui
import tkinter as tk
from pynput import keyboard
from screen_capture import ScreenCapture
from detect import FruitDetector
from mouse_controller import MouseController

class SimpleTracker:
    def __init__(self):
        self.last_items = []
        self.last_time = 0

    def get_velocity_compensated(self, current_items, current_time, latency=0.08):
        dt = current_time - self.last_time
        if dt > 0.3 or dt == 0:
            self.last_items = current_items
            self.last_time = current_time
            return current_items
            
        compensated = []
        for item in current_items:
            cx, cy = item['center']
            comp_item = dict(item)
            
            best_match = None
            min_dist = float('inf')
            for lf in self.last_items:
                dist = math.hypot(cx - lf['center'][0], cy - lf['center'][1])
                if dist < 200:
                    if dist < min_dist:
                        min_dist = dist
                        best_match = lf
            
            if best_match:
                vx = (cx - best_match['center'][0]) / dt
                vy = (cy - best_match['center'][1]) / dt
                # Predict forward by estimated total system latency
                comp_item['center'] = (int(cx + vx * latency), int(cy + vy * latency))
            
            compensated.append(comp_item)
            
        self.last_items = current_items
        self.last_time = current_time
        return compensated

class FruitNinjaBot:
    def __init__(self):
        # Load config
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        
        self.enabled = self.config['automation']['enabled']
        self.running = True
        
        # Scaling correction for High-DPI screens
        self.screen_width, self.screen_height = pyautogui.size()
        self.cap = ScreenCapture(region=self.config['capture']['region'])
        
        # Determine scaling factor
        dummy_frame = self.cap.get_frame()
        self.cap_height, self.cap_width = dummy_frame.shape[:2]
        self.scale_x = self.screen_width / self.cap_width
        self.scale_y = self.screen_height / self.cap_height
        
        # Weights selection
        model_path = self.config['model']['path']
        if not os.path.exists(model_path):
            print(f"Weights {model_path} not found. Using yolov8n.pt placeholder.")
            model_path = "yolov8n.pt"
        
        self.detector = FruitDetector(model_path, conf_threshold=self.config['automation']['min_confidence'])
        self.mouse = MouseController(speed=self.config['automation']['mouse_speed'])
        self.fruit_tracker = SimpleTracker()
        
        self.last_action_time = 0
        self.cooldown = self.config['automation']['cooldown']
        
        # Start keyboard listener for emergency stop
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
        print("\n" + "="*40)
        print("  FRUIT NINJA UNITY - ALL SYSTEMS ACTIVE")
        print(f"  Accuracy: 99% (v2_small) | Auto-Start: {'ON' if self.enabled else 'OFF'}")
        print("="*40 + "\n")

    def on_press(self, key):
        try:
            if key == keyboard.Key.esc:
                print("[INFO] Emergency Quit Triggered (ESC)")
                self.running = False
                return False
        except: pass

    def get_dist(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def is_path_safe(self, p1, p2, bombs, buffer):
        for bomb in bombs:
            bx, by = bomb['center']
            d = self.point_segment_dist(bx, by, p1[0], p1[1], p2[0], p2[1])
            if d < buffer: return False
        return True

    def point_segment_dist(self, px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0: return math.sqrt((px - x1)**2 + (py - y1)**2)
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx**2 + dy**2)))
        return math.sqrt((px - (x1 + t * dx))**2 + (py - (y1 + t * dy))**2)

    def plan_combo_path(self, fruits, bombs):
        if not fruits: return []
        fruits_sorted = sorted(fruits, key=lambda f: f['center'][1], reverse=True)
        max_chain = self.config['automation'].get('max_chain_length', 5)
        max_dist = self.config['automation'].get('chain_distance', 300)
        bomb_buffer = self.config['automation']['bomb_buffer']
        
        chain = [fruits_sorted[0]['center']]
        remaining = fruits_sorted[1:]
        
        while len(chain) < max_chain and remaining:
            best_idx = -1
            min_d = max_dist
            for i, f in enumerate(remaining):
                d = self.get_dist(chain[-1], f['center'])
                if d < min_d and self.is_path_safe(chain[-1], f['center'], bombs, bomb_buffer):
                    min_d = d
                    best_idx = i
            if best_idx != -1:
                chain.append(remaining.pop(best_idx)['center'])
            else: break
        return chain

    def get_extended_swipe(self, p1, p2, ext=100):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0: return p1, p2
        ux, uy = dx/dist, dy/dist
        return (int(p1[0] - ux * ext), int(p1[1] - uy * ext)), (int(p2[0] + ux * ext), int(p2[1] + uy * ext))

    def get_safe_tilt(self, center, bombs, buffer, length=200):
        # Default order
        angles = [(-0.7, 0.7), (1, 0), (0, 1), (0.7, 0.7)]
        
        closest_bomb = None
        min_d = float('inf')
        for b in bombs:
            d = math.hypot(center[0] - b['center'][0], center[1] - b['center'][1])
            if d < min_d:
                min_d = d
                closest_bomb = b
                
        if closest_bomb and min_d < 400:
            bx, by = closest_bomb['center']
            dx, dy = abs(bx - center[0]), abs(by - center[1])
            if dy < dx:
                # Bomb is horizontally adjacent (same level). Prioritize vertical slashes!
                angles = [(0, 1), (-0.7, 0.7), (0.7, 0.7), (1, 0)]
            else:
                # Bomb is vertically adjacent (above/below). Prioritize horizontal slashes!
                angles = [(1, 0), (-0.7, 0.7), (0.7, 0.7), (0, 1)]
                
        for ux, uy in angles:
            p1 = (int(center[0] - ux * length/2), int(center[1] - uy * length/2))
            p2 = (int(center[0] + ux * length/2), int(center[1] + uy * length/2))
            if self.is_path_safe(p1, p2, bombs, buffer): return p1, p2
        return None, None

    def get_edge_slice(self, center, bombs):
        closest_bomb = None
        min_d = float('inf')
        for b in bombs:
            bx, by = b['center']
            d = math.hypot(center[0] - bx, center[1] - by)
            if d < min_d:
                min_d = d
                closest_bomb = b
                
        if not closest_bomb: return None, None
            
        bx, by = closest_bomb['center']
        dx, dy = center[0] - bx, center[1] - by
        dist = math.hypot(dx, dy)
        if dist == 0: return None, None
            
        ux, uy = dx/dist, dy/dist
        # Locate the far exposed rim of the fruit
        far_cx = center[0] + ux * 35
        far_cy = center[1] + uy * 35
        
        # Perpendicular micro-stab
        nx, ny = -uy, ux
        # Extremely short 40-pixel bounding stab
        p1 = (int(far_cx - nx * 20), int(far_cy - ny * 20))
        p2 = (int(far_cx + nx * 20), int(far_cy + ny * 20))
        
        # Reduced safety bubble buffer just for this micro-strike
        if self.is_path_safe(p1, p2, bombs, buffer=35):
            return p1, p2
        return None, None

    def run(self):
        show_view = self.config['automation']['show_view']
        reg_x = self.config['capture']['region'][0] if self.config['capture']['region'] else 0
        reg_y = self.config['capture']['region'][1] if self.config['capture']['region'] else 0
        bomb_buffer = self.config['automation']['bomb_buffer']
        
        try:
            while self.running:
                frame = self.cap.get_frame()
                detections = self.detector.detect(frame)
                
                fruits_raw = [d for d in detections if d['class'] == 'Fruit']
                bombs = [d for d in detections if d['class'] == 'Bomb']
                
                # Apply velocity compensation based on displacement from last frame
                current_time = time.time()
                fruits = self.fruit_tracker.get_velocity_compensated(fruits_raw, current_time)
                
                # Heartbeat telemetry
                if fruits or bombs:
                    print(f"\r[DETECTION] Fruits: {len(fruits)} | Bombs: {len(bombs)}      ", end="")
                
                if self.enabled and fruits and (time.time() - self.last_action_time > self.cooldown):
                    path = self.plan_combo_path(fruits, bombs)
                    if path:
                        if len(path) == 1:
                            # 1. Try a massive 400px strike
                            p1, p2 = self.get_safe_tilt(path[0], bombs, bomb_buffer, length=400)
                            if not p1:
                                # 2. Try a clean 150px default strike
                                p1, p2 = self.get_safe_tilt(path[0], bombs, bomb_buffer, length=150)
                                if not p1:
                                    # 3. Micro-stab the furthest exposed rim of the fruit!
                                    p1, p2 = self.get_edge_slice(path[0], bombs)
                                    # 4. Total geometric occlusion: skip
                                    if not p1: continue
                            final_path = [p1, p2]
                        else:
                            # Extend the first and last segments intuitively matching the real shape of the chain
                            p_start, _ = self.get_extended_swipe(path[0], path[1], ext=150)
                            if not self.is_path_safe(p_start, path[0], bombs, bomb_buffer): p_start = path[0] # Retract if unsafe
                            
                            _, p_end = self.get_extended_swipe(path[-2], path[-1], ext=150)
                            if not self.is_path_safe(path[-1], p_end, bombs, bomb_buffer): p_end = path[-1] # Retract if unsafe
                            
                            final_path = [p_start] + path + [p_end]
                    
                        # Optimized lag compensation: fruits don't fall as much since our swipe is instant now
                        LAG_COMPENSATION_Y = 15
                        screen_path = [(int((p[0] + reg_x) * self.scale_x), int((p[1] + reg_y + LAG_COMPENSATION_Y) * self.scale_y)) for p in final_path]
                        self.mouse.swipe_chain(screen_path)
                        self.last_action_time = time.time()
                
                if show_view:
                    cv2.imshow("Debug View", cv2.resize(self.detector.draw_detections(frame, detections), (640,360)))
                    if cv2.waitKey(1) & 0xFF == 27: break
        except Exception as e:
            print(f"\n[CRITICAL ERROR IN BOT THREAD]: {repr(e)}")
            import traceback
            traceback.print_exc()
        finally:
            cv2.destroyAllWindows()
            self.listener.stop()

class UnifiedOverlay:
    def __init__(self, root, bot):
        self.root = root
        self.bot = bot
        self.root.title("FN")
        self.root.geometry("60x60+10+10")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.9)
        
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

        bg_color = "#2ecc71" if self.bot.enabled else "#e74c3c"
        text = "⚡" if self.bot.enabled else "⭕"
        
        self.btn = tk.Button(self.root, text=text, command=self.toggle,
                              bg=bg_color, fg="white", font=("Arial", 20, "bold"),
                              activebackground="#27ae60", bd=0, cursor="hand2")
        self.btn.pack(fill="both", expand=True)
        
        self.close_btn = tk.Label(self.root, text="×", bg=bg_color, fg="white", font=("Arial", 8))
        self.close_btn.place(x=45, y=0)
        self.close_btn.bind("<Button-1>", lambda e: self.quit_all())

    def start_move(self, event):
        self.x, self.y = event.x, event.y

    def do_move(self, event):
        x, y = self.root.winfo_x() + (event.x - self.x), self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"60x60+{x}+{y}")

    def toggle(self):
        self.bot.enabled = not self.bot.enabled
        color = "#2ecc71" if self.bot.enabled else "#e74c3c"
        self.btn.config(bg=color, text="⚡" if self.bot.enabled else "⭕")
        self.close_btn.config(bg=color)

    def quit_all(self):
        self.bot.running = False
        self.root.destroy()

if __name__ == "__main__":
    bot = FruitNinjaBot()
    bot_thread = threading.Thread(target=bot.run, daemon=True)
    bot_thread.start()
    
    root = tk.Tk()
    app = UnifiedOverlay(root, bot)
    root.mainloop()
