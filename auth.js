
import { auth } from "./firebase.js";

import {
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    sendEmailVerification,
    sendPasswordResetEmail,
    signOut
} from "https://www.gstatic.com/firebasejs/13.2.0/firebase-auth.js";

// Register a new user
export async function signup(email, password) {
    const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
    );

    await sendEmailVerification(userCredential.user);

    return userCredential.user;
}

// Login an existing user
export async function login(email, password) {
    const userCredential = await signInWithEmailAndPassword(
        auth,
        email,
        password
    );

    if (!userCredential.user.emailVerified) {
        await signOut(auth);
        throw new Error("Please verify your email before logging in.");
    }

    return userCredential.user;
}

// Reset forgotten password
export async function resetPassword(email) {
    await sendPasswordResetEmail(auth, email);
}

// Logout
export async function logout() {
    await signOut(auth);
}

console.log("Posture Buddy authentication ready!");
