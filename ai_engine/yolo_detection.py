import cv2
import requests
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")   # small fast model

# Django API endpoint
API_URL = "http://127.0.0.1:8000/api/alerts/create/"

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection
    results = model(frame)

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]

            # YOLO COCO class 67 = cell phone
            if label == "cell phone":

                print("📱 Phone Detected!")

                # Send alert to Django
                data = {
                    "student_name": "Unknown",
                    "hall": "Hall A",
                    "violation_type": "Phone Detected"
                }

                try:
                    requests.post(API_URL, json=data)
                except:
                    print("Server not reachable")

                # Draw red box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)
                cv2.putText(frame, "PHONE DETECTED", (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    cv2.imshow("YOLO Phone Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()