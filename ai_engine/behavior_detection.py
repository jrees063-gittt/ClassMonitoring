import cv2
import mediapipe as mp
import numpy as np
import time
import requests

API_URL = "http://127.0.0.1:8000/api/alerts/create/"

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

cap = cv2.VideoCapture(0)

gaze_start_time = None
current_direction = None

def send_alert(violation):
    data = {
        "student_name": "Unknown",
        "hall": "Hall A",
        "violation_type": violation
    }
    requests.post(API_URL, json=data)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        face = results.multi_face_landmarks[0]

        nose_x = int(face.landmark[1].x * w)
        left_eye = int(face.landmark[33].x * w)
        right_eye = int(face.landmark[263].x * w)

        center = (left_eye + right_eye) // 2

        direction = "CENTER"

        if nose_x < center - 20:
            direction = "LEFT"
        elif nose_x > center + 20:
            direction = "RIGHT"

        # Head Down Detection
        nose_y = int(face.landmark[1].y * h)
        if nose_y > h * 0.6:
            direction = "DOWN"

        # Track duration
        if direction != "CENTER":
            if current_direction != direction:
                gaze_start_time = time.time()
                current_direction = direction
            else:
                duration = time.time() - gaze_start_time
                if duration > 3:
                    print(f"⚠ Looking {direction} for 3+ sec")
                    send_alert(f"Head {direction} Long")
                    gaze_start_time = time.time()
        else:
            current_direction = None

        cv2.putText(frame, f"Direction: {direction}",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0,255,0), 2)

    cv2.imshow("Head Movement Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()