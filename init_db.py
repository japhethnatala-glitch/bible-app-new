import sqlite3
import json

def setup_db():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        credits INTEGER DEFAULT 0
    )
    """)

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

    # Highlights table (new)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS highlights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        verse_id INTEGER,
        action TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(verse_id) REFERENCES verses(id)
    )
    """)

    # Saved verses table (optional, if you want to preload favorites)
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
    print("Database setup complete! Tables created.")

def load_json(file_path, translation):
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for book, chapters in data.items():
        for chapter, verses in chapters.items():
            for verse, text in verses.items():
                cur.execute("""
                    INSERT INTO verses (book, chapter, verse, text, translation)
                    VALUES (?, ?, ?, ?, ?)
                """, (book, int(chapter), int(verse), text, translation))

    conn.commit()
    conn.close()
    print(f"{translation} verses loaded successfully!")

if __name__ == "__main__":
    setup_db()
    load_json("verses.kjv.json", "KJV")
    load_json("verses.web.json", "WEB")
    print("All data imported successfully!")
