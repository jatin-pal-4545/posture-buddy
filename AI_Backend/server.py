
from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# Current posture information
posture_data = {
    "status": "WAITING",
    "good_time": 0,
    "bad_time": 0,
    "total_time": 0,
    "last_updated": None
}

# Store the latest camera frame
latest_frame = None
frame_lock = threading.Lock()


@app.route("/")
def home():
    return "Posture Buddy API is running!"


# Receive posture information
@app.route("/posture", methods=["POST"])
def update_posture():
    global posture_data

    data = request.get_json()

    if not data or data.get("status") not in [
        "GOOD POSTURE", "BAD POSTURE"
    ]:
        return jsonify({"error": "Invalid posture status"}), 400

    posture_data["status"] = data["status"]
    posture_data["good_time"] = data.get("good_time", 0)
    posture_data["bad_time"] = data.get("bad_time", 0)
    posture_data["total_time"] = data.get("total_time", 0)
    posture_data["last_updated"] = datetime.now().isoformat()

    return jsonify({"message": "Posture updated successfully"})


# Get posture information
@app.route("/posture", methods=["GET"])
def get_posture():
    return jsonify(posture_data)


# Receive camera frames from test_posture.py
@app.route("/frame", methods=["POST"])
def receive_frame():
    global latest_frame

    if "frame" not in request.files:
        return jsonify({"error": "No frame received"}), 400

    frame = request.files["frame"].read()

    if not frame:
        return jsonify({"error": "Empty frame"}), 400

    with frame_lock:
        latest_frame = frame

    return jsonify({"message": "Frame received"})


# Stream camera frames to the website
def generate_frames():
    while True:
        with frame_lock:
            frame = latest_frame

        if frame is not None:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                frame +
                b"\r\n"
            )

        time.sleep(0.04)


@app.route("/video_feed")
def video_feed():
    return Response(
        stream_with_context(generate_frames()),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )
