import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session

# ✅ Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for sessions

# ✅ Load config depending on environment
env = os.environ.get("FLASK_ENV", "development")
if env == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

# ---------------------------
# Database initialization
# ---------------------------
def init_db():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # Create verses table
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

    # Create users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        credits INTEGER DEFAULT 0
    )
    """)

    # Create favorites table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        verse_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(verse_id) REFERENCES verses(id)
    )
    """)

    conn.commit()
    conn.close()

# Run initialization at startup
init_db()

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

# ✅ Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name", "Anonymous")

        add_user(name, email)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        conn.close()

        if row:
            session["user_id"] = row["id"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Login failed.", "danger")

    return render_template("login.html")

# ✅ Logout route
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/verse/<translation>")
def verse(translation):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM verses WHERE translation = ? ORDER BY RANDOM() LIMIT 1", (translation,))
    row = cur.fetchone()
    conn.close()

    user_id = session.get("user_id", None)

    if row:
        return render_template("verse.html",
                               verse=row["text"],
                               translation=row["translation"],
                               verse_id=row["id"],
                               user_id=user_id)
    else:
        return render_template("verse.html",
                               verse="No verses found.",
                               translation=translation.upper(),
                               verse_id=None,
                               user_id=user_id)

# ✅ Search route
@app.route("/search/<translation>", methods=["GET", "POST"])
def search(translation):
    results = []
    user_credits = None

    if request.method == "POST":
        keyword = request.form.get("keyword", "").lower()
        email = request.form.get("email")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM verses WHERE translation = ? AND text LIKE ?", (translation, f"%{keyword}%"))
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            results.append(f"{row['book']} {row['chapter']}:{row['verse']} — {row['text']}")

        if email:
            add_user("Anonymous", email)
            add_credits(email, 1)
            user_credits = get_credits(email)

    return render_template("search.html", results=results, translation=translation.upper(), credits=user_credits)

# ✅ Favorites Routes
@app.route("/add_favorite", methods=["POST"])
def add_favorite():
    data = request.get_json()
    user_id = data["user_id"]
    verse_id = data["verse_id"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO favorites (user_id, verse_id) VALUES (?, ?)", (user_id, verse_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

@app.route("/favorites/<int:user_id>")
def favorites(user_id):
    # Protect route: only allow logged-in user to view their own favorites
    if session.get("user_id") != user_id:
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.book, v.chapter, v.verse, v.text, v.translation, f.created_at
        FROM favorites f
        JOIN verses v ON f.verse_id = v.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return render_template("favorites.html", favorites=rows)

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
