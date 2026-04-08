# Fruit Ninja Automation Bot 🍉🥷

An advanced, fully autonomous AI bot designed to play Fruit Ninja with superhuman precision. The bot utilizes real-time computer vision, predictive velocity tracking, complex geometric pathfinding, and spline-interpolated mouse movements to slice fruits and safely avoid bombs.

## ✨ Features

- **Real-Time Object Detection**: Uses a fine-tuned **YOLOv8** model to classify on-screen objects as `Fruit` or `Bomb` with high confidence.
- **Velocity Compensation Extrapolation**: Projects the movement trajectories of falling and flying targets to strike where the fruit *will be*, neutralizing system lag.
- **Smart Pathfinding & Bomb Avoidance**: Mathematically calculates the distance of swipe vectors to bombs. Safely tilts or performs perpendicular "micro-stabs" on exposed rims of fruits closely overlapping with bombs.
- **Combo Chaining**: Automatically groups falling fruits and links them in high-point multi-target combo chains.
- **Organic Spline Swipes**: Replaces jagged, detectable straight lines with dynamically generated **Catmull-Rom splines** and Bezier curves. Ensures fluid, human-like swipes that register flawlessly with the game engine.
- **Ultra-Fast Visual Pipelining**: Uses the `mss` library to grab window frames natively off the OS monitor at high frame rates.
- **HUD Overlay**: Seamless `Tkinter`-based floating overlay to toggle the bot on (⚡) or off (⭕) cleanly, combined with an emergency `ESC` key kill-switch.

## 🛠️ Technology Stack

- **Model**: Ultralytics YOLO (You Only Look Once - version 8 `small`)
- **Computer Vision**: OpenCV (`cv2`)
- **Control Simulation**: PyAutoGUI, Pynput
- **Screen Capture**: MSS
- **Math & Logic**: NumPy, Math

## 📂 Project Structure

- `main.py`: The core heartbeat of the bot. Handles threading, lag-compensation logic, safe pathfinding, and rendering the Tkinter visual overlay.
- `detect.py`: Wraps the YOLOv8 model inference logic. Processes screenshot arrays into normalized dictionaries of fruit/bomb nodes.
- `mouse_controller.py`: The motor-functions. Translates coordinate nodes into smoothly interpolated hardware-level mouse drags avoiding game-engine input rejection.
- `screen_capture.py`: Fast monitor screenshot grabber bypassing standard IO slowness.
- `config.yaml`: Simple unified configuration variables (confidence thresholds, swipe padding, speeds, chain distances).
- `models/`: Directory holding your trained YOLO weights (e.g., `best.pt`).

## 🚀 How to Install Fruit Ninja on Windows

This is currently only supported on Windows machine with specifically Intel processors. Intel and Google have partnered to bring mobile games officially to run like an emulator just like Bluestack.

To get the game for Intel Based Windows Machine you just need to search for the game on Android phone, there will be an option to get invitation for PC runs. Click on it and you will be able to install offcial emulator from Google Play Store for Windows. Then download the Fruit Ninja game from there.

## 🚀 How to Run

1. **Install Requirements**:
   Ensure you have a Python environment set up with necessary packages.
   ```bash
   pip install ultralytics opencv-python numpy pyautogui pynput mss pyyaml
   ```

2. **Configure (Optional)**:
   Adjust settings in `config.yaml` to optimize for your screen resolution, minimum confidence threshold, or bomb avoidance padding.

3. **In-game Setup**:
   Bring up Fruit Ninja on your main monitor.

4. **Launch the Bot**:
   Run the main script.
   ```bash
   python main.py
   ```

5. **Controls**:
   - The green/red floating window controls whether the bot's mouse overrides are Active (⚡) or Paused (⭕). Click to toggle.
   - Press **ESC** on your keyboard to hit the emergency kill switch and terminate the script immediately. 



---
*Built for MVP testing of rapid CV pipeline automation. Not for malicious use.*
