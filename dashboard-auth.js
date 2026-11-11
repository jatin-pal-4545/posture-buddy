
import { auth } from "./firebase.js";

import {
    onAuthStateChanged,
    signOut
} from "https://www.gstatic.com/firebasejs/13.2.0/firebase-auth.js";

// Check whether a user is logged in
onAuthStateChanged(auth, async (user) => {

    // If nobody is logged in, redirect to login
    if (!user) {
        window.location.replace("login.html");
        return;
    }

    // Only verified users can access the dashboard
    if (!user.emailVerified) {
        await signOut(auth);
        window.location.replace("login.html");
        return;
    }

    console.log("Dashboard access granted:", user.email);
});
