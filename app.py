import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------------
# Database initialization
# ---------------------------
def init_db():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # Verses table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS verses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book TEXT,
        chapter INTEGER,
        verse INTEGER,
        text TEXT,
        translation TEXT
    )
    """)

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        credits INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

# ---------------------------
# Helpers
# ---------------------------
def get_user(email):
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, credits FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()
    return user

# ---------------------------
# Routes
# ---------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        user = get_user(email)
        if user:
            session["user_email"] = email
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("User not found. Please register.", "danger")
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_email", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")

    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        flash("Registration successful!", "success")
    except sqlite3.IntegrityError:
        flash("Email already registered.", "danger")
    conn.close()

    return redirect(url_for("index"))

# ✅ Daily verse route
@app.route("/verse/<translation>")
def verse(translation):
    daily = f"Daily verse placeholder for {translation}"
    return render_template("verse.html", translation=translation, daily=daily)

# ✅ All verses route
@app.route("/verses/<translation>")
def verses(translation):
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT book, chapter, verse, text, translation FROM verses WHERE translation = ?", (translation,))
    all_verses = cur.fetchall()
    conn.close()
    return render_template("verses.html", translation=translation, verses=all_verses)

@app.route("/credits")
def credits():
    return render_template("credits.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/help")
def help():
    return render_template("help.html")

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    if not os.path.exists("app.db"):
        init_db()
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
