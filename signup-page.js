
import { signup } from "./auth.js";

const form = document.getElementById("signupForm");
const message = document.getElementById("message");
const button = document.getElementById("signupBtn");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    button.disabled = true;
    button.textContent = "Creating account...";
    message.textContent = "";

    try {
        await signup(email, password);

        message.style.color = "green";
        message.textContent =
            "Account created! Check your email and verify your account before logging in.";

        form.reset();

    } catch (error) {
        message.style.color = "red";
        message.textContent = error.message;

    } finally {
        button.disabled = false;
        button.textContent = "Create Account";
    }
});
