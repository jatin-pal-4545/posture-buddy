
import cv2
import mediapipe as mp
import math
import time
import statistics
import requests
from plyer import notification

# Flask backend
API_URL = "http://127.0.0.1:5000/posture"

FRAME_URL = "http://127.0.0.1:5000/frame"

# Send camera frames 10 times per second
last_frame_upload = 0
frame_upload_interval = 0.1

# MediaPipe setup
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()


def calculate_angle(ear, shoulder, hip):
    a = (ear.x - shoulder.x, ear.y - shoulder.y)
    b = (hip.x - shoulder.x, hip.y - shoulder.y)

    dot = a[0] * b[0] + a[1] * b[1]
    mag_a = math.hypot(*a)
    mag_b = math.hypot(*b)

    if mag_a == 0 or mag_b == 0:
        return None

    cosine = dot / (mag_a * mag_b)
    cosine = max(-1, min(1, cosine))

    return math.degrees(math.acos(cosine))


# Calibration settings
calibration_duration = 5
calibration_angles = []
baseline_angle = None
calibration_start = None

# Detection settings
BAD_THRESHOLD = 12
BAD_DURATION = 5

bad_start_time = None
last_notification = 0
notification_cooldown = 60

status = "CALIBRATING"

# Posture timers (seconds)
good_time = 0
bad_time = 0
last_frame_time = time.time()

# Flask update timer
last_api_update = 0
api_interval = 1

print("Sit upright for 5 seconds...")
print("Press Q to quit.")

with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        current_time = time.time()
        elapsed = min(current_time - last_frame_time, 1)
        last_frame_time = current_time

        angle = None

        if results.pose_landmarks:

            landmarks = results.pose_landmarks.landmark

            mp_draw.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

            sides = [
                (7, 11, 23, "LEFT"),
                (8, 12, 24, "RIGHT")
            ]

            best_side = None
            best_visibility = 0

            for ear_id, shoulder_id, hip_id, name in sides:

                ear = landmarks[ear_id]
                shoulder = landmarks[shoulder_id]
                hip = landmarks[hip_id]

                visibility = min(
                    ear.visibility,
                    shoulder.visibility,
                    hip.visibility
                )

                if visibility > best_visibility:
                    best_visibility = visibility
                    best_side = (ear, shoulder, hip, name)

            if best_side and best_visibility > 0.5:

                ear, shoulder, hip, side = best_side

                angle = calculate_angle(ear, shoulder, hip)

        # Calibration
        if baseline_angle is None:

            if calibration_start is None:
                calibration_start = current_time

            if angle is not None:
                calibration_angles.append(angle)

            if current_time - calibration_start >= calibration_duration:

                if len(calibration_angles) >= 10:
                    baseline_angle = statistics.median(
                        calibration_angles
                    )
                    print("Calibration complete:", baseline_angle)
                    print("Keep sitting upright. Your baseline is:", baseline_angle)

                else:
                    calibration_angles.clear()
                    calibration_start = current_time

            status = "CALIBRATING"

        # Posture monitoring
        elif angle is not None:

            deviation = abs(angle - baseline_angle)
            print(
                f"Current angle: {angle:.1f} | "
                f"Baseline: {baseline_angle:.1f} | "
                f"Deviation: {deviation:.1f}"
            )

            if deviation > BAD_THRESHOLD:

                if bad_start_time is None:
                    bad_start_time = current_time

                bad_duration = current_time - bad_start_time

                if bad_duration >= BAD_DURATION:

                    status = "BAD POSTURE"

                    if current_time - last_notification >= notification_cooldown:

                        notification.notify(
                            title="Posture Buddy ⚠️",
                            message="You are sitting incorrectly! Please correct your posture.",
                            app_name="Posture Buddy",
                            timeout=10
                        )

                        print("Posture alert triggered!")
                        last_notification = current_time

                else:
                    status = "WARNING"

            else:
                bad_start_time = None
                status = "GOOD POSTURE"

        else:
            status = "BODY NOT DETECTED"
            bad_start_time = None

        # Count posture time
        if status == "GOOD POSTURE":
            good_time += elapsed

        elif status in ["WARNING", "BAD POSTURE"]:
            bad_time += elapsed

        total_time = good_time + bad_time

        print("Current status:", status)

        # Send data to Flask every second
        if current_time - last_api_update >= api_interval:

            if status in ["GOOD POSTURE", "WARNING", "BAD POSTURE"]:

                api_status = (
                    "GOOD POSTURE"
                    if status == "GOOD POSTURE"
                    else "BAD POSTURE"
                )

                payload = {
                    "status": api_status,
                    "good_time": round(good_time),
                    "bad_time": round(bad_time),
                    "total_time": round(total_time)
                }

                try:
                    response = requests.post(
                        API_URL,
                        json=payload,
                        timeout=0.5
                    )

                    response.raise_for_status()
                    print("Dashboard updated:", api_status)

                except requests.RequestException as error:
                    print("Flask connection error:", error)

            last_api_update = current_time

        # Display information
        color = (0, 255, 0)

        if status in ["BAD POSTURE", "WARNING"]:
            color = (0, 0, 255)

        if status == "CALIBRATING":
            color = (255, 255, 0)

        cv2.putText(
            frame,
            status,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

        if angle is not None:
            cv2.putText(
                frame,
                f"Angle: {angle:.1f}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

        if baseline_angle is not None:
            cv2.putText(
                frame,
                f"Baseline: {baseline_angle:.1f}",
                (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

        cv2.putText(
            frame,
            f"Good: {int(good_time)}s  Bad: {int(bad_time)}s",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # Send processed camera frame to Flask
        if current_time - last_frame_upload >= frame_upload_interval:

            success, buffer = cv2.imencode(
                ".jpg",
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, 70]
            )

            if success:
                try:
                    requests.post(
                        FRAME_URL,
                        files={
                            "frame": (
                                "frame.jpg",
                                buffer.tobytes(),
                                "image/jpeg"
                            )
                        },
                        timeout=1
                    )

                except requests.RequestException as error:
                    print("Camera upload error:", error)

            last_frame_upload = current_time

        cv2.imshow("Posture Buddy AI", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
