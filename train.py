from ultralytics import YOLO
import os
import shutil

def train_model():
    # Upgrade to YOLOv8s (Small) for much better accuracy on your RTX 4050
    # The 'Small' model is deeper than 'Nano' and handles complex backgrounds better.
    model = YOLO('yolov8s.pt')

    print("Starting Model Accuracy Upgrade training...")
    # Increase to 120 epochs for better convergence
    results = model.train(
        data='dataset.yaml',
        epochs=120,
        imgsz=640,
        batch=-1,      # auto-calculate batch size for your GPU (RTX 4050)
        device=0,      # Use the Nvidia GPU
        name='fruit_ninja_v2_small',
        augment=True,  # Heavy data augmentation to handle the "Board" background
        patience=30,   # Early stopping if no improvement for 30 epochs
        cache=True,    # Cache images in RAM for faster training
        plots=True
    )

    print("Training complete.")
    
    # Copy best weights to models/ folder
    best_weights = os.path.join(results.save_dir, 'weights', 'best.pt')
    if os.path.exists(best_weights):
        # Backup the old best.pt if it exists
        if os.path.exists('models/best.pt'):
            os.rename('models/best.pt', 'models/best_nano_backup.pt')
            
        shutil.copy(best_weights, 'models/best.pt')
        print(f"New High-Accuracy weights saved to models/best.pt")

if __name__ == "__main__":
    train_model()
