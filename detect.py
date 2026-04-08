from ultralytics import YOLO
import cv2
import numpy as np

class FruitDetector:
    def __init__(self, model_path, conf_threshold=0.5):
        self.model = YOLO(model_path)
        self.conf = conf_threshold

    def detect(self, frame):
        """
        Runs inference on the frame.
        Returns list of detections: [{'box': (x1, y1, x2, y2), 'conf': c, 'class': name, 'center': (cx, cy)}]
        """
        results = self.model(frame, conf=self.conf, imgsz=640, verbose=False)[0]
        detections = []
        
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = box.conf[0].cpu().item()
            cls = int(box.cls[0].cpu().item())
            name = results.names[cls]
            
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            detections.append({
                'box': (int(x1), int(y1), int(x2), int(y2)),
                'conf': conf,
                'class': name,
                'center': (int(center_x), int(center_y))
            })
            
        return detections

    def draw_detections(self, frame, detections):
        for det in detections:
            x1, y1, x2, y2 = det['box']
            label = f"{det['class']} {det['conf']:.2f}"
            color = (0, 255, 0) if det['class'] == 'Fruit' else (0, 0, 255)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.circle(frame, det['center'], 5, color, -1)
            
        return frame
