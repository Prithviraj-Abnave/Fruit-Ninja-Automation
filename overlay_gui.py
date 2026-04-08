import tkinter as tk
import threading
from main import FruitNinjaBot
import yaml
import os

class MinimalToggle:
    def __init__(self, root):
        self.root = root
        self.root.title("FN")
        # Tiny window: 60x60, placed at top right by default
        self.root.geometry("60x60+100+100")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)  # No borders
        self.root.attributes("-alpha", 0.8) # Semi-transparent
        
        # Draggable logic
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

        self.bot_active = False
        self.stop_event = threading.Event()
        self.bot_thread = None
        
        self.setup_ui()

    def setup_ui(self):
        # Create a "Circular" button using a frame with rounded feel
        self.btn = tk.Button(self.root, text="⭕", command=self.toggle_bot,
                              bg="#e74c3c", fg="white", font=("Arial", 20, "bold"),
                              activebackground="#c0392b", bd=0, cursor="hand2")
        self.btn.pack(fill="both", expand=True)
        
        # Add a tiny "X" to close
        self.close_btn = tk.Label(self.root, text="×", bg="#e74c3c", fg="white", font=("Arial", 8))
        self.close_btn.place(x=45, y=0)
        self.close_btn.bind("<Button-1>", lambda e: self.quit_app())

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"60x60+{x}+{y}")

    def toggle_bot(self):
        if not self.bot_active:
            self.start_bot()
        else:
            self.stop_bot()

    def start_bot(self):
        self.bot_active = True
        self.stop_event.clear()
        self.btn.config(bg="#2ecc71", activebackground="#27ae60", text="⚡")
        self.close_btn.config(bg="#2ecc71")
        
        # Start bot thread
        self.bot_instance = FruitNinjaBot()
        self.bot_instance.enabled = True # Force enable
        self.bot_thread = threading.Thread(target=self.bot_instance.run, daemon=True)
        self.bot_thread.start()

    def stop_bot(self):
        self.bot_active = False
        self.stop_event.set()
        if hasattr(self, 'bot_instance'):
            self.bot_instance.running = False # Signal loop to stop
            
        self.btn.config(bg="#e74c3c", activebackground="#c0392b", text="⭕")
        self.close_btn.config(bg="#e74c3c")

    def quit_app(self):
        self.stop_bot()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MinimalToggle(root)
    root.mainloop()
