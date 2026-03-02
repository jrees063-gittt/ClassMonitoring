import cv2
import mediapipe as mp
import numpy as np
import face_recognition
import os
import time
import requests
from ultralytics import YOLO

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000/api/alerts/create/"
HALL_NAME = "Hall A"
SCREENSHOT_DIR = "evidence"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ---------------- LOAD FACE RECOGNITION ----------------
known_encodings = []
known_names = []

for file in os.listdir("known_faces"):
    img = face_recognition.load_image_file(f"known_faces/{file}")
    encoding = face_recognition.face_encodings(img)[0]
    known_encodings.append(encoding)
    known_names.append(file.split(".")[0])

# ---------------- LOAD MODELS ----------------
mp_face_mesh = mp.solutions.face_mesh
mp_pose = mp.solutions.pose

face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
pose = mp_pose.Pose()

yolo = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(0)

behavior_score = 0
last_alert_time = 0

def save_screenshot(frame, violation):
    filename = f"{SCREENSHOT_DIR}/{int(time.time())}_{violation}.jpg"
    cv2.imwrite(filename, frame)
    return filename

def send_alert(student, violation):
    global last_alert_time

    if time.time() - last_alert_time < 10:
        return

    last_alert_time = time.time()

    screenshot_path = save_screenshot(frame, violation)

    data = {
        "student_name": student,
        "hall": HALL_NAME,
        "violation_type": violation
    }

    try:
        requests.post(API_URL, json=data)
        print("Alert Sent:", violation)
    except:
        print("Server not reachable")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ---------------- FACE RECOGNITION ----------------
    face_locations = face_recognition.face_locations(rgb)
    face_encodings = face_recognition.face_encodings(rgb, face_locations)

    student_name = "Unknown"

    for encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, encoding)
        if True in matches:
            student_name = known_names[matches.index(True)]

    # ---------------- HEAD DETECTION ----------------
    mesh_results = face_mesh.process(rgb)

    if mesh_results.multi_face_landmarks:
        face = mesh_results.multi_face_landmarks[0]

        h, w, _ = frame.shape

        nose_x = int(face.landmark[1].x * w)
        left_eye = int(face.landmark[33].x * w)
        right_eye = int(face.landmark[263].x * w)

        center = (left_eye + right_eye) // 2

        direction = "CENTER"

        if nose_x < center - 20:
            direction = "LEFT"
        elif nose_x > center + 20:
            direction = "RIGHT"

        nose_y = int(face.landmark[1].y * h)
        if nose_y > h * 0.6:
            direction = "DOWN"

        if direction != "CENTER":
            behavior_score += 1
            if behavior_score > 15:
                send_alert(student_name, f"Head {direction} Suspicious")
                behavior_score = 0

        cv2.putText(frame, f"Head: {direction}",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0,255,0), 2)

    # ---------------- BODY DETECTION ----------------
    pose_results = pose.process(rgb)

    if pose_results.pose_landmarks:
        left_shoulder = pose_results.pose_landmarks.landmark[11]
        right_shoulder = pose_results.pose_landmarks.landmark[12]

        diff = abs(left_shoulder.x - right_shoulder.x)

        if diff > 0.4:
            behavior_score += 2
            if behavior_score > 20:
                send_alert(student_name, "Excessive Body Rotation")
                behavior_score = 0

    # ---------------- PHONE DETECTION ----------------
    results = yolo(frame)

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            label = yolo.names[class_id]

            if label == "cell phone":
                behavior_score += 5
                if behavior_score > 10:
                    send_alert(student_name, "Phone Detected")
                    behavior_score = 0

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)

    cv2.putText(frame, f"Student: {student_name}",
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (255,255,0), 2)

    cv2.imshow("AI Master Monitoring Engine", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()