import os
import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for, session, g

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

    # Saved verses table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS saved_verses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        verse_id INTEGER,
        translation TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(verse_id) REFERENCES verses(id)
    )
    """)

    conn.commit()
    conn.close()

# ✅ Run init_db immediately so tables exist on Render
init_db()

# ---------------------------
# Load credits globally
# ---------------------------
@app.before_request
def load_user_credits():
    g.credits = None
    if "user_id" in session:
        conn = sqlite3.connect("app.db", timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT credits FROM users WHERE id = ?", (session["user_id"],))
        row = cur.fetchone()
        conn.close()
        if row:
            g.credits = row[0]

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

# ✅ Books → Chapters → Verses navigation
@app.route("/books/<translation>")
def books(translation):
    conn = sqlite3.connect("app.db", timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT book FROM verses WHERE translation = ?", (translation,))
    books = [row[0] for row in cur.fetchall()]
    conn.close()
    return render_template("books.html", translation=translation, books=books, credits=g.credits)

@app.route("/chapters/<translation>/<book>")
def chapters(translation, book):
    conn = sqlite3.connect("app.db", timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT chapter FROM verses WHERE translation = ? AND book = ?", (translation, book))
    chapters = [row[0] for row in cur.fetchall()]
    conn.close()
    return render_template("chapters.html", translation=translation, book=book, chapters=chapters, credits=g.credits)

@app.route("/chapter/<translation>/<book>/<int:chapter>")
def chapter(translation, book, chapter):
    conn = sqlite3.connect("app.db", timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT id, verse, text FROM verses WHERE translation = ? AND book = ? AND chapter = ?",
                (translation, book, chapter))
    verses = cur.fetchall()
    conn.close()
    return render_template("chapter.html", translation=translation, book=book, chapter=chapter, verses=verses, credits=g.credits)

@app.route("/search/<translation>", methods=["GET", "POST"])
def search(translation):
    results = []
    if request.method == "POST":
        keyword = request.form.get("keyword")
        conn = sqlite3.connect("app.db", timeout=5)
        cur = conn.cursor()
        if keyword:
            cur.execute("SELECT book, chapter, verse, text FROM verses WHERE translation = ? AND text LIKE ?", (translation, f"%{keyword}%"))
            verses_found = cur.fetchall()
            results = [f"{book} {chapter}:{verse} - {text}" for book, chapter, verse, text in verses_found]
        conn.close()
    return render_template("search.html", translation=translation, results=results, credits=g.credits)

@app.route("/save/<int:verse_id>/<translation>", methods=["POST"])
def save_verse(verse_id, translation):
    if "user_id" not in session:
        flash("Please log in to save verses.", "warning")
        return redirect(url_for("login"))

    conn = sqlite3.connect("app.db", timeout=5)
    cur = conn.cursor()

    cur.execute("SELECT credits FROM users WHERE id = ?", (session["user_id"],))
    row = cur.fetchone()
    if not row or row[0] <= 0:
        flash("Not enough credits. Please buy more.", "danger")
        conn.close()
        return redirect(url_for("credits"))

    cur.execute("UPDATE users SET credits = credits - 1 WHERE id = ?", (session["user_id"],))
    cur.execute("INSERT INTO saved_verses (user_id, verse_id, translation) VALUES (?, ?, ?)",
                (session["user_id"], verse_id, translation))
    conn.commit()
    conn.close()

    flash("Verse saved successfully!", "success")
    return redirect(url_for("favorites"))

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
    conn = sqlite3.connect("app.db", timeout=5)
    cur = conn.cursor()
    cur.execute("""
        SELECT verses.book, verses.chapter, verses.verse, verses.text, verses.translation
        FROM saved_verses
        JOIN verses ON saved_verses.verse_id = verses.id
        WHERE saved_verses.user_id = ?
    """, (session["user_id"],))
    favorites = cur.fetchall()
    conn.close()
    return render_template("favorites.html", favorites=favorites, credits=g.credits)

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/credits")
def credits():
    return render_template("credits.html")

@app.route("/payment_callback", methods=["POST"])
def payment_callback():
    data = request.json
    email = data.get("order_description")
    amount = float(data.get("price_amount", 0))
    credits_to_add = 0
    if amount == 5:
        credits_to_add = 50
    elif amount == 10:
        credits_to_add = 120
    if credits_to_add > 0 and email:
        conn = sqlite3.connect("app.db", timeout=5)
        cur = conn.cursor()
        cur.execute("UPDATE users SET credits = credits + ? WHERE email = ?", (credits_to_add, email))
        conn.commit()
        conn.close()
    return {"status": "success"}, 200

# ---------------------------
# Debugging helpers
# ---------------------------
@app.route("/debug/routes")
def debug_routes():
    return str(app.url_map)

@app.route("/debug/verses/<translation>")
def debug_verses(translation):
    conn = sqlite3.connect("app.db", timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), MIN(book), MAX(book) FROM verses WHERE translation = ?", (translation,))
    result = cur.fetchone()
    conn.close()
    return f"Total verses: {result[0]}, First book: {result[1]}, Last book: {result[2]}"

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    # ✅ Only run Flask locally; Render uses Gunicorn
    # ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    # ✅ Only run Flask locally; Render uses Gunicorn in production
    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
