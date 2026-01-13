from ultralytics import YOLO
from typing import List
from backend.app.models import DetectionResult

# Load a pretrained model (e.g., yolov8n.pt)
# Load a pretrained model
# It will download on first use
# Ultralytics will auto-select GPU if available, but let's be explicit in logs
# Load a pretrained model (e.g., yolov8x.pt - Extra Large for Best Accuracy)
# It will download on first use (approx 130MB+)
# Ultralytics will auto-select GPU if available.
model = YOLO("backend/yolov8n.pt")
import torch
if torch.cuda.is_available():
    model.to('cuda')
    print("✅ YOLOv8 pushed to GPU.")
else:
    print("⚠️ YOLOv8 running on CPU.")

def run_detection(image_path: str) -> List[DetectionResult]:
    """
    Runs YOLOv8 detection on the image.
    Returns classified objects.
    """
    # Run inference
    results = model(image_path)
    
    output = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Class ID and Name
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist() # [x1, y1, x2, y2]
            
            output.append(DetectionResult(
                label=label,
                confidence=round(conf, 2),
                box=[round(x, 1) for x in xyxy]
            ))
            
    return output
