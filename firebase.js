
import { initializeApp } from "https://www.gstatic.com/firebasejs/13.2.0/firebase-app.js";

import { getAuth } from "https://www.gstatic.com/firebasejs/13.2.0/firebase-auth.js";

import { getFirestore } from "https://www.gstatic.com/firebasejs/13.2.0/firebase-firestore.js";

// Replace this configuration with the exact values
// from your Firebase web app configuration.

const firebaseConfig = {
    apiKey: "AIzaSyCUoOHpXUet_M0xY6rzWw7ZIiXcH3MjGqI",
    authDomain: "posture-buddy-9a5b8.firebaseapp.com",
    projectId: "posture-buddy-9a5b8",
    storageBucket: "posture-buddy-9a5b8.firebasestorage.app",
    messagingSenderId: "881085322226",
    appId: "1:881085322226:web:86dbf7dc8aa6e3851d516b",
    measurementId: "G-XWGPGBV646"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Authentication and Firestore
export const auth = getAuth(app);
export const db = getFirestore(app);

console.log("Firebase connected successfully!");
