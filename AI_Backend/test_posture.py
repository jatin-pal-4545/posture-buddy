
import cv2
import mediapipe as mp
import math
import time
import statistics
from plyer import notification

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

# Detection settings
BAD_THRESHOLD = 12
BAD_DURATION = 5

bad_start_time = None
last_notification = 0
notification_cooldown = 60

status = "CALIBRATING"

print("Sit upright for 5 seconds...")
print("Press Q to quit.")

def calibrate():
    pass

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

                angle = calculate_angle(
                    ear, shoulder, hip
                )

        
        # Calibration
        if baseline_angle is None:

            if not hasattr(calibrate, "start"):
                calibrate.start = current_time

            if angle is not None:
                calibration_angles.append(angle)

            if current_time - calibrate.start >= calibration_duration:

                if len(calibration_angles) >= 10:
                    baseline_angle = statistics.median(
                        calibration_angles
                    )
                    print("Calibration complete:", baseline_angle)
                else:
                    calibration_angles.clear()
                    calibrate.start = current_time

            status = "CALIBRATING"

        # Posture monitoring
        elif angle is not None:

            deviation = abs(angle - baseline_angle)

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

        cv2.imshow("Posture Buddy AI", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
