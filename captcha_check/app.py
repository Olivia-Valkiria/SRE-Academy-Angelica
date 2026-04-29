from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests, os
from dotenv import load_dotenv

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

load_dotenv()  # loads .env variables (confidential keys are stored here, and not in the codebase, not exposed publicly)

# Google reCAPTCHA keys
RECAPTCHA_SITE_KEY = "6LcQEA4sAAAAAGIRz8DJ-TTU1tGq9gmP1IDFFDie"  # Public key for client-side
SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")  # Confidential key for server-side verification

# Dummy user for example
USER_DB = {
    "angelica": "sre2323" # In a real application, hashed passwords and a secure database should be encouraged.
}

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        recaptcha_response = request.form.get("g-recaptcha-response")

        # --- Verify reCAPTCHA ---
        payload = {
            "secret": SECRET_KEY,
            "response": recaptcha_response
        }
        recaptcha_verify = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data=payload
        ).json()

        if not recaptcha_verify.get("success"):
            flash("Please verify that you're not a robot.", "danger")
            return redirect(url_for("login"))

        # --- Authenticate user ---
        if USER_DB.get(username) == password:
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html", site_key=RECAPTCHA_SITE_KEY)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return f"Welcome, {session['user']}! You have successfully logged in."

if __name__ == "__main__":
    app.run(debug=True)
