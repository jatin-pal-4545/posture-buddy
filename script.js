
const API_URL = "http://127.0.0.1:5000/posture";

// Display today's date
const dateElement = document.getElementById("date");

if (dateElement) {
    dateElement.textContent = new Date().toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric"
    });
}

// Convert seconds into HH:MM:SS
function formatTime(seconds) {
    seconds = Math.floor(Number(seconds) || 0);

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return (
        String(hours).padStart(2, "0") + ":" +
        String(minutes).padStart(2, "0") + ":" +
        String(secs).padStart(2, "0")
    );
}

// Get live data from Flask
async function updateDashboard() {
    try {
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error("Server response: " + response.status);
        }

        const data = await response.json();

        document.getElementById("goodTime").textContent =
            formatTime(data.good_time);

        document.getElementById("badTime").textContent =
            formatTime(data.bad_time);

        document.getElementById("totalTime").textContent =
            formatTime(data.total_time);

        const statusElement = document.getElementById("postureStatus");
        const indicator = document.getElementById("postureIndicator");

        if (statusElement && indicator) {
            statusElement.textContent = data.status;

            indicator.classList.remove("good", "bad");

            if (data.status === "GOOD POSTURE") {
                indicator.classList.add("good");
            } else if (data.status === "BAD POSTURE") {
                indicator.classList.add("bad");
            }
        }

        console.log("Dashboard updated:", data);

    } catch (error) {
        console.error("Could not connect to Flask:", error);
    }
}

// Fetch data every second
updateDashboard();
setInterval(updateDashboard, 1000);

// Notification button
const notificationBtn = document.getElementById("notificationBtn");

if (notificationBtn) {
    notificationBtn.addEventListener("click", function () {
        if ("Notification" in window) {
            Notification.requestPermission().then(permission => {
                if (permission === "granted") {
                    new Notification("Posture Buddy", {
                        body: "Your posture monitoring dashboard is ready!"
                    });
                } else {
                    alert("Please allow notifications in your browser.");
                }
            });
        } else {
            alert("Browser notifications are not supported.");
        }
    });
}

console.log("Posture Buddy dashboard loaded!");
