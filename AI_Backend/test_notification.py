
from plyer import notification

print("Sending test notification...")

notification.notify(
    title="Posture Buddy",
    message="Test successful! Your notification system is working.",
    app_name="Posture Buddy",
    timeout=10
)

print("Notification command executed.")
