import os
import random
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for

# ✅ Load environment variables
load_dotenv()

app = Flask(__name__)

# ✅ Load config depending on environment
env = os.environ.get("FLASK_ENV", "development")
if env == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

# ---------------------------
# Database connection + helpers
# ---------------------------

def get_db_connection():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn

def add_user(name, email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()

def add_credits(email, amount):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET credits = credits + ? WHERE email = ?", (amount, email))
    conn.commit()
    conn.close()

def get_credits(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT credits FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

# ---------------------------
# Helper functions for verses
# ---------------------------

def load_verses(translation="KJV"):
    filename = f"verses_{translation.lower()}.txt"
    try:
        with open(filename, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def format_line(line):
    line = line.strip()
    if line.startswith("==="):
        book_name = line.strip("= ").title()
        return f"<h2 style='color:darkblue'>{book_name}</h2>"
    elif "World English Bible" in line or "King James Version" in line:
        return f"<h3 style='color:green'>{line}</h3>"
    else:
        return f"<p>{line}</p>"

# ---------------------------
# Routes
# ---------------------------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        with open("messages.txt", "a", encoding="utf-8") as f:
            f.write(f"Name: {name}\nEmail: {email}\nMessage: {message}\n---\n")

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")

@app.route("/verse/<translation>")
def verse(translation):
    verses = load_verses(translation)
    daily_verse = random.choice(verses) if verses else "No verses found."
    return render_template("verse.html", verse=daily_verse, translation=translation.upper())

@app.route("/search/<translation>", methods=["GET", "POST"])
def search(translation):
    verses = load_verses(translation)
    results = []
    user_credits = None
    if request.method == "POST":
        keyword = request.form.get("keyword", "").lower()
        email = request.form.get("email")
        for v in verses:
            if keyword in v.lower():
                results.append(format_line(v))
        if email:
            add_user("Anonymous", email)
            add_credits(email, 1)  # reward 1 credit per search
            user_credits = get_credits(email)
    return render_template("search.html", results=results, translation=translation.upper(), credits=user_credits)

@app.route("/search_book/<translation>", methods=["GET", "POST"])
def search_book(translation):
    verses = load_verses(translation)
    results = []
    if request.method == "POST":
        bookname = request.form.get("bookname", "").lower()
        for v in verses:
            if bookname in v.lower():
                results.append(format_line(v))
    return render_template("search_book.html", results=results, translation=translation.upper())

@app.route("/verses/<translation>")
def verses(translation):
    verses = load_verses(translation)
    formatted = [format_line(v) for v in verses]
    return render_template("verses.html", verses=formatted, translation=translation.upper())

# ✅ Legal Pages
@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# ✅ Offline Page
@app.route("/offline")
def offline():
    return render_template("offline.html")

# ---------------------------
# Run the app
# ---------------------------

if __name__ == "__main__":
    app.run(debug=True)
