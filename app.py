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

@app.route("/verse/<translation>")
def verse(translation):
    daily = f"Daily verse placeholder for {translation}"
    return render_template("verse.html", translation=translation, daily=daily)

# ✅ Updated Verses Route with proper book order
@app.route("/verses/<translation>")
def verses(translation):
    conn = sqlite3.connect("app.db", timeout=5)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, book, chapter, verse, text, translation
        FROM verses
        WHERE translation = ?
        ORDER BY 
            CASE book
                WHEN 'Genesis' THEN 1
                WHEN 'Exodus' THEN 2
                WHEN 'Leviticus' THEN 3
                WHEN 'Numbers' THEN 4
                WHEN 'Deuteronomy' THEN 5
                WHEN 'Joshua' THEN 6
                WHEN 'Judges' THEN 7
                WHEN 'Ruth' THEN 8
                WHEN '1 Samuel' THEN 9
                WHEN '2 Samuel' THEN 10
                WHEN '1 Kings' THEN 11
                WHEN '2 Kings' THEN 12
                WHEN '1 Chronicles' THEN 13
                WHEN '2 Chronicles' THEN 14
                WHEN 'Ezra' THEN 15
                WHEN 'Nehemiah' THEN 16
                WHEN 'Esther' THEN 17
                WHEN 'Job' THEN 18
                WHEN 'Psalms' THEN 19
                WHEN 'Proverbs' THEN 20
                WHEN 'Ecclesiastes' THEN 21
                WHEN 'Song of Solomon' THEN 22
                WHEN 'Isaiah' THEN 23
                WHEN 'Jeremiah' THEN 24
                WHEN 'Lamentations' THEN 25
                WHEN 'Ezekiel' THEN 26
                WHEN 'Daniel' THEN 27
                WHEN 'Hosea' THEN 28
                WHEN 'Joel' THEN 29
                WHEN 'Amos' THEN 30
                WHEN 'Obadiah' THEN 31
                WHEN 'Jonah' THEN 32
                WHEN 'Micah' THEN 33
                WHEN 'Nahum' THEN 34
                WHEN 'Habakkuk' THEN 35
                WHEN 'Zephaniah' THEN 36
                WHEN 'Haggai' THEN 37
                WHEN 'Zechariah' THEN 38
                WHEN 'Malachi' THEN 39
                WHEN 'Matthew' THEN 40
                WHEN 'Mark' THEN 41
                WHEN 'Luke' THEN 42
                WHEN 'John' THEN 43
                WHEN 'Acts' THEN 44
                WHEN 'Romans' THEN 45
                WHEN '1 Corinthians' THEN 46
                WHEN '2 Corinthians' THEN 47
                WHEN 'Galatians' THEN 48
                WHEN 'Ephesians' THEN 49
                WHEN 'Philippians' THEN 50
                WHEN 'Colossians' THEN 51
                WHEN '1 Thessalonians' THEN 52
                WHEN '2 Thessalonians' THEN 53
                WHEN '1 Timothy' THEN 54
                WHEN '2 Timothy' THEN 55
                WHEN 'Titus' THEN 56
                WHEN 'Philemon' THEN 57
                WHEN 'Hebrews' THEN 58
                WHEN 'James' THEN 59
                WHEN '1 Peter' THEN 60
                WHEN '2 Peter' THEN 61
                WHEN '1 John' THEN 62
                WHEN '2 John' THEN 63
                WHEN '3 John' THEN 64
                WHEN 'Jude' THEN 65
                WHEN 'Revelation' THEN 66
            END,
            chapter, verse
    """, (translation,))
    all_verses = cur.fetchall()
    conn.close()
    return render_template("verses.html", translation=translation, verses=all_verses)

# ✅ The rest of your routes remain unchanged...
# (search, save_verse, login, favorites, logout, credits, payment_callback, about, contact, faq, privacy, terms, help)

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
