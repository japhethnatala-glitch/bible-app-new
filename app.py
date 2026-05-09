import os
import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------------
# Database initialization
# ---------------------------
def init_db():
    conn = sqlite3.connect("app.db", timeout=5)
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

# ✅ Run init_db immediately so tables exist on Render
init_db()

# ---------------------------
# Routes
# ---------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        if not name or not email:
            flash("Name and email are required.", "warning")
            return redirect(url_for("index"))

        conn = sqlite3.connect("app.db", timeout=5)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
            session["user_id"] = cur.lastrowid
            flash("Registration successful!", "success")
            return redirect(url_for("home"))
        except sqlite3.IntegrityError:
            flash("Email already registered. Please log in instead.", "danger")
            return redirect(url_for("login"))
        except Exception as e:
            conn.rollback()
            flash(f"Unexpected error: {e}", "danger")
            return redirect(url_for("index"))
        finally:
            conn.close()

    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/verse/<translation>")
def verse(translation):
    daily = f"Daily verse placeholder for {translation}"
    return render_template("verse.html", translation=translation, daily=daily)

@app.route("/verses/<translation>")
def verses(translation):
    conn = sqlite3.connect("app.db", timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT book, chapter, verse, text, translation FROM verses WHERE translation = ?", (translation,))
    all_verses = cur.fetchall()
    conn.close()
    return render_template("verses.html", translation=translation, verses=all_verses)

@app.route("/search/<translation>", methods=["GET", "POST"])
def search(translation):
    results = []
    credits = None

    if request.method == "POST":
        keyword = request.form.get("keyword")
        email = request.form.get("email")

        conn = sqlite3.connect("app.db", timeout=5)
        cur = conn.cursor()

        if "user_id" in session:
            cur.execute("SELECT credits FROM users WHERE id = ?", (session["user_id"],))
            row = cur.fetchone()
            if row:
                credits = row[0]

        if keyword:
            cur.execute("SELECT book, chapter, verse, text FROM verses WHERE translation = ? AND text LIKE ?", (translation, f"%{keyword}%"))
            verses_found = cur.fetchall()
            results = [f"{book} {chapter}:{verse} - {text}" for book, chapter, verse, text in verses_found]

        conn.close()

    return render_template("search.html", translation=translation, results=results, credits=credits)

# ✅ New login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")

        conn = sqlite3.connect("app.db", timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Email not found. Please register first.", "danger")
            return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/favorites")
def favorites():
    if "user_id" not in session:
        flash("You must be logged in to view favorites.", "warning")
        return redirect(url_for("login"))
    return render_template("favorites.html", favorites=[])

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
