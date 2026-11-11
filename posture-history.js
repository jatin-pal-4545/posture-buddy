
import { auth, db } from "./firebase.js";

import {
    collection,
    addDoc,
    serverTimestamp
} from "https://www.gstatic.com/firebasejs/13.2.0/firebase-firestore.js";

const API_URL = "http://127.0.0.1:5000/posture";

let saveInterval = null;

async function savePostureData(user) {
    try {
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error("Could not fetch posture data");
        }

        const data = await response.json();

        const goodTime = Number(data.good_time) || 0;
        const badTime = Number(data.bad_time) || 0;
        const totalTime = Number(data.total_time) || 0;

        const postureScore = totalTime > 0
            ? Math.round((goodTime / totalTime) * 100)
            : 0;

        const record = {
            status: data.status,
            good_time: goodTime,
            bad_time: badTime,
            total_time: totalTime,
            posture_score: postureScore,
            recorded_at: serverTimestamp()
        };

        await addDoc(
            collection(db, "users", user.uid, "postureHistory"),
            record
        );

        console.log("Posture history saved to Firebase!", record);

    } catch (error) {
        console.error("Firebase history error:", error);
    }
}

// Wait until Firebase confirms the logged-in user
auth.onAuthStateChanged(user => {

    if (saveInterval) {
        clearInterval(saveInterval);
        saveInterval = null;
    }

    if (!user || !user.emailVerified) {
        console.log("No verified user. History saving stopped.");
        return;
    }

    console.log("Firebase history enabled for:", user.email);

    // Save the first summary immediately
    savePostureData(user);

    // Save another summary every 60 seconds
    saveInterval = setInterval(() => {
        savePostureData(user);
    }, 60000);
});
