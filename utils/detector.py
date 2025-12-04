from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect_bus(frame):
    results = model(frame)
    for r in results:
        for box in r.boxes:
            cls = int(box.cls)
            label = model.names[cls]
            if label.lower() in ["bus", "coach", "truck"]:
                return True
    return False
