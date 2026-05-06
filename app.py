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
            flash("Email already registered.", "danger")
            return redirect(url_for("index"))
        except Exception as e:
            conn.rollback()
            flash(f"Error: {e}", "danger")
            return redirect(url_for("index"))
        finally:
            conn.close()

    return render_template("index.html")   # Registration page

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

@app.route("/favorites")
def favorites():
    if "user_id" not in session:
        flash("You must be logged in to view favorites.", "warning")
        return redirect(url_for("login"))
    return render_template("favorites.html", favorites=[])

@app.route("/login")
def login():
    return render_template("login.html")

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
    init_db()  # Always initialize tables at startup
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
