
// Display current date

const dateElement = document.getElementById("date");

const today = new Date();

dateElement.textContent = today.toLocaleDateString(
    "en-IN",
    {
        day: "numeric",
        month: "short",
        year: "numeric"
    }
);


// Demo timers

let goodSeconds = 9258;
let badSeconds = 2532;

function formatTime(seconds) {

    let hours = Math.floor(seconds / 3600);

    let minutes = Math.floor(
        (seconds % 3600) / 60
    );

    let secs = seconds % 60;

    return (
        String(hours).padStart(2, "0") + ":" +
        String(minutes).padStart(2, "0") + ":" +
        String(secs).padStart(2, "0")
    );
}


// Update demo dashboard

function updateDashboard() {

    goodSeconds++;

    const totalSeconds = goodSeconds + badSeconds;

    document.getElementById("goodTime").textContent =
        formatTime(goodSeconds);

    document.getElementById("badTime").textContent =
        formatTime(badSeconds);

    document.getElementById("totalTime").textContent =
        formatTime(totalSeconds);

}

setInterval(updateDashboard, 1000);


// Notification button

const notificationBtn =
    document.getElementById("notificationBtn");

notificationBtn.addEventListener("click", function() {

    if ("Notification" in window) {

        Notification.requestPermission().then(permission => {

            if (permission === "granted") {

                new Notification("Posture Buddy", {
                    body: "Your posture monitoring dashboard is ready!",
                });

            } else {

                alert("Please allow notifications in your browser.");

            }

        });

    } else {

        alert("Browser notifications are not supported.");

    }

});


// Demo notification

console.log("Posture Buddy dashboard loaded successfully!");