
import { login, resetPassword } from "./auth.js";

const form = document.getElementById("loginForm");
const message = document.getElementById("message");
const button = document.getElementById("loginBtn");

function showMessage(text, color) {
    message.textContent = text;
    message.style.color = color;
}

// Login functionality
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    button.disabled = true;
    button.textContent = "Logging in...";

    try {
        await login(email, password);

        showMessage("Login successful! Opening dashboard...", "green");

        window.location.href = "index.html";

    } catch (error) {
        showMessage(error.message, "red");

    } finally {
        button.disabled = false;
        button.textContent = "Login";
    }
});

// Forgot password functionality
document.getElementById("forgotPassword")
.addEventListener("click", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();

    if (!email) {
        showMessage("Please enter your email address first.", "red");
        return;
    }

    try {
        await resetPassword(email);

        showMessage(
            "Password reset link sent! Check your email.",
            "green"
        );

    } catch (error) {
        showMessage(error.message, "red");
    }
});
